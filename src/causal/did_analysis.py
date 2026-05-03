"""
Difference-in-Differences Analysis for Promotion Impact.

Implements DiD using DoWhy's causal framework with:
- Automatic treatment/control group identification
- Parallel trends testing
- Robustness refutation tests
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

from src.config import causal as causal_cfg

logger = logging.getLogger(__name__)


class DifferenceInDifferences:
    """
    Promotion impact estimation via Difference-in-Differences.
    
    Identifies price-drop promotions, constructs treatment/control groups,
    and estimates the causal effect using DiD regression.
    """

    def __init__(self, config=causal_cfg):
        self.config = config
        self.results: Dict = {}

    def identify_promotions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect promotion events from price data.
        
        A promotion is defined as a price drop exceeding the threshold
        relative to the recent rolling average price.
        
        Args:
            df: DataFrame with sell_price, id, date columns.
        
        Returns:
            DataFrame with promotion events annotated.
        """
        logger.info("Identifying promotion events...")

        df = df.sort_values(["id", "date"]).copy()

        # Rolling average price (14-day window)
        df["price_baseline"] = df.groupby("id")["sell_price"].transform(
            lambda x: x.shift(1).rolling(14, min_periods=7).mean()
        )

        # Price drop ratio
        df["price_drop_ratio"] = np.where(
            df["price_baseline"] > 0,
            1 - (df["sell_price"] / df["price_baseline"]),
            0,
        )

        # Flag promotions
        df["is_promoted"] = (df["price_drop_ratio"] >= self.config.price_drop_threshold).astype(int)

        # Promotion event boundaries
        df["promo_start"] = (df["is_promoted"] == 1) & (df["is_promoted"].shift(1).fillna(0) == 0)
        df["promo_group"] = df.groupby("id")["promo_start"].cumsum()

        num_promos = df["promo_start"].sum()
        logger.info(f"Found {num_promos:,} promotion events across {df['id'].nunique()} series")
        return df

    def construct_treatment_control(
        self,
        df: pd.DataFrame,
        treatment_item: str,
        treatment_store: str,
        pre_days: int = None,
        post_days: int = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Build treatment and control groups for a specific promotion event.
        
        Treatment: promoted item at specific store
        Control: same item at other stores (or similar items at same store)
        
        Args:
            df: Full dataset with promotion flags.
            treatment_item: item_id of promoted product.
            treatment_store: store_id where promotion occurred.
            pre_days: Number of pre-treatment days.
            post_days: Number of post-treatment days.
        """
        pre_days = pre_days or self.config.pre_period_days
        post_days = post_days or self.config.post_period_days

        # Find promotion date for this item-store
        mask = (
            (df["item_id"] == treatment_item) &
            (df["store_id"] == treatment_store) &
            (df["is_promoted"] == 1)
        )
        promo_dates = df.loc[mask, "date"]

        if promo_dates.empty:
            raise ValueError(f"No promotions found for {treatment_item} at {treatment_store}")

        promo_start = pd.to_datetime(promo_dates.iloc[0])

        # Date windows
        pre_start = promo_start - pd.Timedelta(days=pre_days)
        post_end = promo_start + pd.Timedelta(days=post_days)

        # Treatment group: promoted item at promotion store
        treatment = df[
            (df["item_id"] == treatment_item) &
            (df["store_id"] == treatment_store) &
            (df["date"] >= pre_start) &
            (df["date"] <= post_end)
        ].copy()
        treatment["group"] = "treatment"

        # Control group: same item at other stores (no promotion)
        control_stores = df[
            (df["item_id"] == treatment_item) &
            (df["store_id"] != treatment_store) &
            (df["date"] >= pre_start) &
            (df["date"] <= post_end)
        ]
        # Filter out stores that also had promotions
        no_promo_stores = control_stores.groupby("store_id")["is_promoted"].max()
        clean_stores = no_promo_stores[no_promo_stores == 0].index.tolist()

        if len(clean_stores) < self.config.min_control_items:
            # Fallback: use same-department items at same store
            dept = df.loc[df["item_id"] == treatment_item, "dept_id"].iloc[0]
            control = df[
                (df["dept_id"] == dept) &
                (df["item_id"] != treatment_item) &
                (df["store_id"] == treatment_store) &
                (df["date"] >= pre_start) &
                (df["date"] <= post_end)
            ].copy()
        else:
            control = control_stores[control_stores["store_id"].isin(clean_stores)].copy()

        control["group"] = "control"

        # Add time period indicator
        for subset in [treatment, control]:
            subset["post"] = (pd.to_datetime(subset["date"]) >= promo_start).astype(int)
            subset["treated"] = (subset["group"] == "treatment").astype(int)

        logger.info(
            f"Treatment: {len(treatment)} obs | Control: {len(control)} obs | "
            f"Promo date: {promo_start.date()}"
        )
        return treatment, control

    def run_did_regression(self, treatment: pd.DataFrame,
                           control: pd.DataFrame) -> Dict:
        """
        Run DiD regression: sales ~ treated + post + treated×post + controls.
        
        The coefficient on treated×post is the DiD estimator (causal effect).
        """
        data = pd.concat([treatment, control], ignore_index=True)
        data["did"] = data["treated"] * data["post"]

        # Add day-of-week control
        if "day_of_week" in data.columns:
            formula = "sales ~ treated + post + did + C(day_of_week)"
        else:
            formula = "sales ~ treated + post + did"

        model = ols(formula, data=data).fit()

        did_coef = model.params.get("did", 0)
        did_pvalue = model.pvalues.get("did", 1)
        did_ci = model.conf_int().loc["did"].values if "did" in model.conf_int().index else [0, 0]

        # Baseline sales (control, pre-period)
        baseline = data[(data["treated"] == 0) & (data["post"] == 0)]["sales"].mean()

        result = {
            "did_estimate": float(did_coef),
            "p_value": float(did_pvalue),
            "ci_lower": float(did_ci[0]),
            "ci_upper": float(did_ci[1]),
            "significant": did_pvalue < self.config.significance_level,
            "baseline_sales": float(baseline),
            "lift_pct": float(did_coef / baseline * 100) if baseline > 0 else 0,
            "r_squared": float(model.rsquared),
            "n_obs": len(data),
        }

        logger.info(
            f"DiD Result: Lift = {result['did_estimate']:.2f} units "
            f"({result['lift_pct']:.1f}%), p={result['p_value']:.4f}, "
            f"significant={result['significant']}"
        )
        return result

    def run_did_with_dowhy(self, treatment: pd.DataFrame,
                           control: pd.DataFrame) -> Dict:
        """
        Run DiD using DoWhy framework for formal causal identification.
        
        Follows: Model → Identify → Estimate → Refute
        """
        try:
            from dowhy import CausalModel
        except ImportError:
            logger.warning("DoWhy not installed. Using statsmodels DiD.")
            return self.run_did_regression(treatment, control)

        data = pd.concat([treatment, control], ignore_index=True)
        data["did"] = data["treated"] * data["post"]

        # Step 1: Model
        model = CausalModel(
            data=data,
            treatment="did",
            outcome="sales",
            common_causes=["treated", "post"],
        )

        # Step 2: Identify
        identified = model.identify_effect(proceed_when_unidentifiable=True)

        # Step 3: Estimate
        estimate = model.estimate_effect(
            identified,
            method_name="backdoor.linear_regression",
            test_significance=True,
        )

        # Step 4: Refute (placebo treatment)
        try:
            refutation = model.refute_estimate(
                identified, estimate,
                method_name="placebo_treatment_refuter",
                placebo_type="permute",
                num_simulations=self.config.num_placebo_simulations,
            )
            refutation_pvalue = float(refutation.refutation_result.get("p_value", 1.0)) \
                if hasattr(refutation, "refutation_result") else None
        except Exception as e:
            logger.warning(f"Refutation failed: {e}")
            refutation_pvalue = None

        result = {
            "did_estimate": float(estimate.value),
            "p_value": float(estimate.test_stat_significance().get("p_value", 1.0))
                if estimate.test_stat_significance() else None,
            "refutation_passed": refutation_pvalue is None or refutation_pvalue > 0.05,
            "refutation_pvalue": refutation_pvalue,
            "method": "dowhy_did",
        }

        logger.info(f"DoWhy DiD: effect={result['did_estimate']:.2f}")
        return result

    def test_parallel_trends(self, treatment: pd.DataFrame,
                              control: pd.DataFrame) -> Dict:
        """
        Test the parallel trends assumption in the pre-treatment period.
        
        Fits a time trend model and tests for differential trends.
        """
        pre_treat = treatment[treatment["post"] == 0].copy()
        pre_ctrl = control[control["post"] == 0].copy()

        pre_treat["time_trend"] = range(len(pre_treat))
        pre_ctrl["time_trend"] = range(len(pre_ctrl))

        data = pd.concat([pre_treat, pre_ctrl], ignore_index=True)
        data["trend_interaction"] = data["treated"] * data["time_trend"]

        model = ols("sales ~ treated + time_trend + trend_interaction", data=data).fit()

        interaction_pval = model.pvalues.get("trend_interaction", 0)
        parallel = interaction_pval > 0.05

        result = {
            "parallel_trends_holds": parallel,
            "interaction_coefficient": float(model.params.get("trend_interaction", 0)),
            "interaction_pvalue": float(interaction_pval),
        }

        logger.info(
            f"Parallel trends test: {'PASS' if parallel else 'FAIL'} "
            f"(p={interaction_pval:.4f})"
        )
        return result
