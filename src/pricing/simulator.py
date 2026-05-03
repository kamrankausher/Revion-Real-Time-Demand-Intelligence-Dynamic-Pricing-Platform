"""
Pricing Simulation Environment.

Creates a realistic simulation using M5 historical data to test
the LinUCB bandit pricing strategy.
"""

import logging
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from src.config import pricing as pricing_cfg
from src.pricing.demand_model import DemandModel

logger = logging.getLogger(__name__)


class PricingSimulator:
    """Simulates a pricing environment using historical M5 data."""

    def __init__(self, demand_model: DemandModel, config=pricing_cfg):
        self.demand_model = demand_model
        self.config = config
        self.rng = np.random.RandomState(42)

    def build_context(self, row: pd.Series, forecast: float = 0) -> np.ndarray:
        """
        Build context vector for bandit from a data row.
        
        Context includes: forecast, price features, calendar, store encoding.
        Pads/truncates to config.context_dim.
        """
        features = []

        # Demand forecast
        features.append(forecast if forecast > 0 else row.get("sales", 0))

        # Price features
        features.append(row.get("sell_price", 0))
        features.append(row.get("price_ratio_cat", 1.0))

        # Calendar
        features.append(row.get("day_of_week", 0))
        features.append(row.get("month", 0))
        features.append(row.get("is_weekend", 0))

        # SNAP
        features.append(row.get("snap_CA", 0))
        features.append(row.get("snap_TX", 0))
        features.append(row.get("snap_WI", 0))

        # Category encoded
        features.append(row.get("cat_id_encoded", 0))
        features.append(row.get("dept_id_encoded", 0))
        features.append(row.get("store_id_encoded", 0))

        # Rolling features
        features.append(row.get("sales_roll_7_mean", 0))
        features.append(row.get("sales_roll_28_mean", 0))
        features.append(row.get("sales_lag_7", 0))

        # Pad or truncate
        context = np.array(features[:self.config.context_dim], dtype=np.float64)
        if len(context) < self.config.context_dim:
            context = np.pad(context, (0, self.config.context_dim - len(context)))

        # Normalize
        norm = np.linalg.norm(context)
        if norm > 0:
            context = context / norm

        return context

    def simulate_demand(self, base_demand: float, base_price: float,
                        price_multiplier: float, segment: str = "") -> float:
        """Simulate demand at a given price point with noise."""
        new_price = base_price * price_multiplier
        expected_demand = self.demand_model.predict_demand(
            base_demand, base_price, new_price, segment
        )
        # Add noise (Poisson for count data)
        noisy_demand = max(0, self.rng.poisson(max(0.1, expected_demand)))
        return float(noisy_demand)

    def compute_reward(self, demand: float, price: float) -> float:
        """Compute revenue reward: price × demand."""
        return demand * price

    def get_optimal_reward(self, base_demand: float, base_price: float,
                           segment: str = "") -> float:
        """Compute oracle optimal reward (for regret calculation)."""
        best_revenue = 0
        for mult in self.config.price_multipliers:
            new_price = base_price * mult
            demand = self.demand_model.predict_demand(
                base_demand, base_price, new_price, segment
            )
            revenue = demand * new_price
            best_revenue = max(best_revenue, revenue)
        return best_revenue

    def run_episode(self, df: pd.DataFrame, agent,
                    n_rounds: Optional[int] = None) -> Dict:
        """
        Run a pricing simulation episode.
        
        Args:
            df: Historical data to sample contexts from.
            agent: LinUCB agent.
            n_rounds: Number of pricing decisions.
        
        Returns:
            Episode results with rewards and regret.
        """
        n_rounds = n_rounds or min(self.config.num_rounds, len(df))
        sampled = df.sample(n=n_rounds, replace=True, random_state=42).reset_index(drop=True)

        rewards = []
        optimal_rewards = []

        for i in range(n_rounds):
            row = sampled.iloc[i]
            base_demand = float(row.get("sales", 1))
            base_price = float(row.get("sell_price", 1))
            segment = str(row.get("dept_id", ""))

            if base_price <= 0:
                continue

            # Build context
            context = self.build_context(row)

            # Agent selects arm
            arm_idx, price_mult = agent.select_arm(context)

            # Simulate demand and compute reward
            demand = self.simulate_demand(base_demand, base_price, price_mult, segment)
            actual_price = base_price * price_mult
            reward = self.compute_reward(demand, actual_price)

            # Update agent
            agent.update(arm_idx, context, reward)

            # Track optimal
            opt_reward = self.get_optimal_reward(base_demand, base_price, segment)
            rewards.append(reward)
            optimal_rewards.append(opt_reward)

        rewards = np.array(rewards)
        optimal_rewards = np.array(optimal_rewards)

        return {
            "total_reward": float(rewards.sum()),
            "avg_reward": float(rewards.mean()),
            "total_optimal": float(optimal_rewards.sum()),
            "cumulative_regret": float((optimal_rewards - rewards).sum()),
            "regret_per_round": float((optimal_rewards - rewards).mean()),
            "n_rounds": len(rewards),
            "arm_stats": agent.get_arm_stats(),
        }
