"""
LinUCB Contextual Bandit for Dynamic Pricing.

Implements the Linear Upper Confidence Bound algorithm for
selecting optimal price points based on contextual features.
"""

import logging
from typing import List, Optional, Tuple

import numpy as np

from src.config import pricing as pricing_cfg

logger = logging.getLogger(__name__)


class LinUCBArm:
    """Single arm (price point) in the LinUCB bandit."""

    def __init__(self, arm_id: int, d: int, alpha: float):
        self.arm_id = arm_id
        self.alpha = alpha
        self.d = d

        # A = d×d identity matrix (regularization)
        self.A = np.eye(d)
        # b = d-dimensional zero vector
        self.b = np.zeros(d)

        self.theta: Optional[np.ndarray] = None
        self.n_pulls = 0

    def get_ucb(self, context: np.ndarray) -> float:
        """
        Compute UCB score for this arm given context.
        
        UCB = θᵀx + α * √(xᵀA⁻¹x)
        
        Uses np.linalg.solve for numerical stability instead of inversion.
        """
        # θ = A⁻¹b (solve Aθ = b)
        self.theta = np.linalg.solve(self.A, self.b)

        # Exploitation: θᵀx
        exploitation = self.theta @ context

        # Exploration: α * √(xᵀA⁻¹x)
        A_inv_x = np.linalg.solve(self.A, context)
        exploration = self.alpha * np.sqrt(context @ A_inv_x)

        return exploitation + exploration

    def update(self, context: np.ndarray, reward: float) -> None:
        """Update arm parameters after observing reward."""
        self.A += np.outer(context, context)
        self.b += reward * context
        self.n_pulls += 1


class LinUCBAgent:
    """
    LinUCB contextual bandit for dynamic pricing.
    
    Each arm represents a discrete price multiplier.
    Context encodes demand forecast, product features, and time signals.
    """

    def __init__(self, config=pricing_cfg):
        self.config = config
        self.d = config.context_dim
        self.alpha = config.alpha
        self.price_multipliers = list(config.price_multipliers)
        self.n_arms = len(self.price_multipliers)

        self.arms = [
            LinUCBArm(i, self.d, self.alpha)
            for i in range(self.n_arms)
        ]

        self.history: List[dict] = []

    def select_arm(self, context: np.ndarray) -> Tuple[int, float]:
        """
        Select the arm with highest UCB score.
        
        Args:
            context: Feature vector of dimension d.
        
        Returns:
            Tuple of (arm_index, price_multiplier).
        """
        if len(context) != self.d:
            raise ValueError(f"Context dim {len(context)} != expected {self.d}")

        ucb_scores = [arm.get_ucb(context) for arm in self.arms]
        best_arm = int(np.argmax(ucb_scores))
        price_mult = self.price_multipliers[best_arm]

        return best_arm, price_mult

    def update(self, arm_idx: int, context: np.ndarray, reward: float) -> None:
        """Update the selected arm with observed reward."""
        self.arms[arm_idx].update(context, reward)
        self.history.append({
            "arm": arm_idx,
            "price_multiplier": self.price_multipliers[arm_idx],
            "reward": reward,
        })

    def get_arm_stats(self) -> List[dict]:
        """Get statistics for each arm."""
        return [
            {
                "arm_id": arm.arm_id,
                "price_multiplier": self.price_multipliers[arm.arm_id],
                "n_pulls": arm.n_pulls,
                "estimated_theta_norm": float(np.linalg.norm(arm.theta))
                    if arm.theta is not None else 0,
            }
            for arm in self.arms
        ]

    def get_cumulative_reward(self) -> np.ndarray:
        """Get cumulative reward over time."""
        rewards = [h["reward"] for h in self.history]
        return np.cumsum(rewards)

    def get_regret(self, optimal_rewards: np.ndarray) -> np.ndarray:
        """Compute cumulative regret relative to oracle."""
        actual = np.array([h["reward"] for h in self.history])
        return np.cumsum(optimal_rewards[:len(actual)] - actual)
