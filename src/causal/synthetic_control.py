"""
Synthetic Control Method for store-level promotion analysis.

Constructs a synthetic counterfactual by optimally weighting
control stores to match the pre-treatment pattern of the treated store.
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.config import causal as causal_cfg

logger = logging.getLogger(__name__)


class SyntheticControlAnalyzer:
    """Synthetic control for estimating store-level promotion effects."""

    def __init__(self, config=causal_cfg):
        self.config = config
        self.weights: Optional[np.ndarray] = None
        self.control_stores: Optional[List[str]] = None

    def prepare_panel(self, df: pd.DataFrame, treated_store: str,
                      target_col: str = "sales",
                      time_col: str = "date") -> Dict[str, pd.DataFrame]:
        """Prepare panel data for synthetic control."""
        # Aggregate to store-day level
        store_daily = df.groupby(["store_id", time_col])[target_col].sum().reset_index()
        store_pivot = store_daily.pivot(index=time_col, columns="store_id", values=target_col)
        store_pivot = store_pivot.fillna(0)

        self.control_stores = [s for s in store_pivot.columns if s != treated_store]

        return {
            "treated": store_pivot[[treated_store]],
            "control": store_pivot[self.control_stores],
            "full": store_pivot,
        }

    def find_optimal_weights(self, treated_pre: np.ndarray,
                              control_pre: np.ndarray) -> np.ndarray:
        """Find weights that minimize distance between treated and synthetic control."""
        n_controls = control_pre.shape[1]

        def objective(w):
            synthetic = control_pre @ w
            return np.sum((treated_pre.flatten() - synthetic) ** 2)

        # Constraints: weights sum to 1, all non-negative
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        bounds = [(0, 1)] * n_controls
        w0 = np.ones(n_controls) / n_controls

        result = minimize(objective, w0, method="SLSQP",
                         bounds=bounds, constraints=constraints)

        self.weights = result.x
        logger.info(f"Optimal weights found. Top stores: "
                    f"{sorted(zip(self.control_stores, self.weights), key=lambda x: -x[1])[:3]}")
        return self.weights

    def estimate_effect(self, df: pd.DataFrame, treated_store: str,
                        treatment_date: str, target_col: str = "sales") -> Dict:
        """Run full synthetic control analysis."""
        panel = self.prepare_panel(df, treated_store, target_col)
        treatment_dt = pd.to_datetime(treatment_date)

        treated = panel["treated"].values
        control = panel["control"].values
        dates = panel["full"].index

        pre_mask = pd.to_datetime(dates) < treatment_dt
        post_mask = ~pre_mask

        # Fit weights on pre-period
        self.find_optimal_weights(treated[pre_mask], control[pre_mask])

        # Construct synthetic control
        synthetic = control @ self.weights

        # Treatment effect = treated - synthetic
        effect = treated.flatten() - synthetic
        att = float(np.mean(effect[post_mask]))
        pre_rmse = float(np.sqrt(np.mean(effect[pre_mask] ** 2)))

        result = {
            "att": att,
            "pre_treatment_rmse": pre_rmse,
            "att_relative": float(att / np.mean(treated[pre_mask])) * 100 if np.mean(treated[pre_mask]) > 0 else 0,
            "treated_store": treated_store,
            "treatment_date": treatment_date,
            "n_pre_periods": int(pre_mask.sum()),
            "n_post_periods": int(post_mask.sum()),
            "weights": dict(zip(self.control_stores, self.weights.tolist())),
        }

        logger.info(f"Synthetic Control ATT: {att:.2f} ({result['att_relative']:.1f}%)")
        return result

    def placebo_test(self, df: pd.DataFrame, treated_store: str,
                     treatment_date: str, target_col: str = "sales") -> Dict:
        """Run placebo tests by applying treatment to each control store."""
        results = []
        for store in self.control_stores:
            try:
                analyzer = SyntheticControlAnalyzer(self.config)
                result = analyzer.estimate_effect(df, store, treatment_date, target_col)
                results.append({"store": store, "att": result["att"]})
            except Exception:
                continue

        if not results:
            return {"placebo_passed": False, "reason": "no_valid_placebos"}

        placebo_atts = [r["att"] for r in results]
        true_result = self.estimate_effect(df, treated_store, treatment_date, target_col)
        true_att = true_result["att"]

        # P-value: fraction of placebos with |ATT| >= |true ATT|
        p_value = np.mean([abs(a) >= abs(true_att) for a in placebo_atts])

        return {
            "placebo_p_value": float(p_value),
            "placebo_passed": p_value < 0.1,
            "true_att": true_att,
            "placebo_atts": placebo_atts,
        }
