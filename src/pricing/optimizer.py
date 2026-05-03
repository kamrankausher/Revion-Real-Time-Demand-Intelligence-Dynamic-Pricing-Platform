"""
Dynamic Pricing Optimizer.

Orchestrates the bandit learning loop, elasticity estimation,
and convergence analysis.
"""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import pricing as pricing_cfg, PROJECT_ROOT
from src.pricing.linucb_bandit import LinUCBAgent
from src.pricing.demand_model import DemandModel
from src.pricing.simulator import PricingSimulator

logger = logging.getLogger(__name__)
PLOTS_DIR = PROJECT_ROOT / "notebooks" / "pricing_plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


class PricingOptimizer:
    """End-to-end dynamic pricing optimization pipeline."""

    def __init__(self, config=pricing_cfg):
        self.config = config
        self.demand_model = DemandModel()
        self.agent = LinUCBAgent(config)
        self.simulator = PricingSimulator(self.demand_model, config)

    def run(self, df: pd.DataFrame, n_rounds: Optional[int] = None) -> Dict:
        """
        Run complete pricing optimization.
        
        Steps:
        1. Estimate price elasticities
        2. Run bandit simulation
        3. Analyze convergence
        4. Generate plots
        """
        logger.info("=" * 60)
        logger.info("Starting pricing optimization...")

        # Step 1: Estimate elasticities
        logger.info("Estimating price elasticities...")
        elasticity_df = self.demand_model.estimate_elasticity(df)

        # Step 2: Run simulation
        logger.info("Running bandit simulation...")
        episode_results = self.simulator.run_episode(df, self.agent, n_rounds)

        # Step 3: Convergence analysis
        convergence = self._analyze_convergence()

        # Step 4: Generate visualizations
        self._plot_results(episode_results)

        results = {
            "elasticities": elasticity_df.to_dict() if not elasticity_df.empty else {},
            "episode": episode_results,
            "convergence": convergence,
        }

        logger.info(f"Optimization complete. Total reward: {episode_results['total_reward']:.0f}, "
                    f"Regret: {episode_results['cumulative_regret']:.0f}")
        return results

    def _analyze_convergence(self) -> Dict:
        """Analyze if the bandit has converged to optimal policy."""
        if not self.agent.history:
            return {}

        rewards = [h["reward"] for h in self.agent.history]
        window = 100

        if len(rewards) < window * 2:
            return {"converged": False, "reason": "insufficient_data"}

        # Compare recent vs early rewards
        early = np.mean(rewards[:window])
        recent = np.mean(rewards[-window:])
        improvement = (recent - early) / (early + 1e-8)

        # Check arm distribution stability
        recent_arms = [h["arm"] for h in self.agent.history[-window:]]
        arm_entropy = -sum(
            (np.array(recent_arms) == a).mean() * np.log((np.array(recent_arms) == a).mean() + 1e-8)
            for a in range(self.agent.n_arms)
        )

        return {
            "early_avg_reward": float(early),
            "recent_avg_reward": float(recent),
            "improvement_pct": float(improvement * 100),
            "arm_entropy": float(arm_entropy),
            "converged": improvement > 0.05 and arm_entropy < 1.5,
        }

    def _plot_results(self, results: Dict) -> None:
        """Generate pricing analysis plots."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Cumulative reward
        cum_reward = self.agent.get_cumulative_reward()
        axes[0, 0].plot(cum_reward, linewidth=1)
        axes[0, 0].set_title("Cumulative Revenue")
        axes[0, 0].set_xlabel("Round")

        # 2. Arm selection frequency
        arm_counts = [arm["n_pulls"] for arm in results["arm_stats"]]
        arm_labels = [f"{arm['price_multiplier']:.2f}x" for arm in results["arm_stats"]]
        axes[0, 1].bar(arm_labels, arm_counts, color="#4CAF50", alpha=0.8)
        axes[0, 1].set_title("Price Point Selection Frequency")
        axes[0, 1].tick_params(axis="x", rotation=45)

        # 3. Rolling average reward
        rewards = [h["reward"] for h in self.agent.history]
        if len(rewards) > 100:
            rolling = pd.Series(rewards).rolling(100).mean()
            axes[1, 0].plot(rolling, linewidth=1)
            axes[1, 0].set_title("Rolling Avg Revenue (100-round window)")

        # 4. Revenue curve example
        if self.demand_model.elasticities:
            segment = list(self.demand_model.elasticities.keys())[0]
            curve = self.demand_model.get_revenue_curve(5.0, 3.0, segment)
            axes[1, 1].plot(curve["price"], curve["revenue"], "b-", linewidth=2)
            axes[1, 1].axvline(x=curve.loc[curve["revenue"].idxmax(), "price"],
                              color="red", linestyle="--", label="Optimal")
            axes[1, 1].set_title(f"Revenue Curve ({segment})")
            axes[1, 1].set_xlabel("Price")
            axes[1, 1].legend()

        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "pricing_results.png", dpi=150)
        plt.close()

    def recommend_price(self, context: np.ndarray, base_price: float) -> Dict:
        """Get price recommendation for a given context."""
        arm_idx, multiplier = self.agent.select_arm(context)
        recommended_price = base_price * multiplier

        return {
            "recommended_price": float(recommended_price),
            "price_multiplier": float(multiplier),
            "base_price": float(base_price),
            "arm_index": arm_idx,
        }
