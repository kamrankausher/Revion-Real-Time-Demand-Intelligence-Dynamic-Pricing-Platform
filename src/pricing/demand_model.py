"""
Price-Demand Elasticity Model.

Estimates price elasticity per product segment using log-linear demand models.
Used to shape bandit rewards and validate pricing decisions.
"""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.config import pricing as pricing_cfg

logger = logging.getLogger(__name__)


class DemandModel:
    """Log-linear demand model for price elasticity estimation."""

    def __init__(self, default_elasticity: float = pricing_cfg.default_elasticity):
        self.default_elasticity = default_elasticity
        self.elasticities: Dict[str, float] = {}
        self.models: Dict[str, sm.OLS] = {}

    def estimate_elasticity(self, df: pd.DataFrame, group_col: str = "dept_id") -> pd.DataFrame:
        """
        Estimate price elasticity per product segment.
        
        Model: ln(sales+1) = β₀ + β₁·ln(price) + β₂·features + ε
        Elasticity = β₁
        """
        logger.info(f"Estimating price elasticity by {group_col}...")

        results = []
        for group, gdf in df.groupby(group_col):
            gdf = gdf.dropna(subset=["sell_price", "sales"])
            gdf = gdf[gdf["sell_price"] > 0]

            if len(gdf) < 100:
                self.elasticities[str(group)] = self.default_elasticity
                continue

            # Log-linear model
            y = np.log1p(gdf["sales"].values)
            X_cols = ["sell_price"]

            # Add controls if available
            controls = ["is_weekend", "month", "snap_CA", "snap_TX", "snap_WI"]
            X_cols += [c for c in controls if c in gdf.columns]

            X = gdf[X_cols].copy()
            X["log_price"] = np.log(X["sell_price"])
            X = X.drop("sell_price", axis=1)
            X = sm.add_constant(X)

            try:
                model = sm.OLS(y, X).fit()
                elasticity = float(model.params.get("log_price", self.default_elasticity))
                pvalue = float(model.pvalues.get("log_price", 1.0))

                self.elasticities[str(group)] = elasticity
                self.models[str(group)] = model

                results.append({
                    "group": str(group),
                    "elasticity": elasticity,
                    "p_value": pvalue,
                    "r_squared": float(model.rsquared),
                    "n_obs": len(gdf),
                    "significant": pvalue < 0.05,
                })
            except Exception as e:
                logger.debug(f"Elasticity estimation failed for {group}: {e}")
                self.elasticities[str(group)] = self.default_elasticity

        results_df = pd.DataFrame(results)
        if not results_df.empty:
            logger.info(f"Elasticity range: [{results_df['elasticity'].min():.2f}, "
                        f"{results_df['elasticity'].max():.2f}]")
        return results_df

    def predict_demand(self, base_demand: float, base_price: float,
                       new_price: float, segment: str = "") -> float:
        """
        Predict demand at a new price point using elasticity.
        
        demand_new = demand_base × (price_new / price_base) ^ elasticity
        """
        elasticity = self.elasticities.get(segment, self.default_elasticity)

        if base_price <= 0 or new_price <= 0:
            return base_demand

        price_ratio = new_price / base_price
        predicted = base_demand * (price_ratio ** elasticity)
        return max(0, predicted)

    def get_revenue_curve(self, base_demand: float, base_price: float,
                          segment: str = "", n_points: int = 50) -> pd.DataFrame:
        """Generate revenue curve across price points."""
        price_range = np.linspace(base_price * 0.5, base_price * 1.5, n_points)
        demands = [self.predict_demand(base_demand, base_price, p, segment) for p in price_range]
        revenues = [p * d for p, d in zip(price_range, demands)]

        return pd.DataFrame({
            "price": price_range, "demand": demands, "revenue": revenues,
        })
