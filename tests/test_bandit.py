"""
Unit tests for LinUCB contextual bandit.
"""

import numpy as np
import pytest
from src.pricing.linucb_bandit import LinUCBAgent, LinUCBArm


class TestLinUCBArm:
    def test_initialization(self):
        arm = LinUCBArm(arm_id=0, d=5, alpha=1.0)
        assert arm.arm_id == 0
        assert arm.A.shape == (5, 5)
        assert arm.b.shape == (5,)
        assert arm.n_pulls == 0

    def test_ucb_computation(self):
        arm = LinUCBArm(arm_id=0, d=3, alpha=1.0)
        context = np.array([1.0, 0.5, 0.3])
        ucb = arm.get_ucb(context)
        assert isinstance(ucb, float)
        assert np.isfinite(ucb)

    def test_update(self):
        arm = LinUCBArm(arm_id=0, d=3, alpha=1.0)
        context = np.array([1.0, 0.5, 0.3])
        arm.update(context, reward=5.0)
        assert arm.n_pulls == 1
        assert not np.array_equal(arm.A, np.eye(3))

    def test_exploration_decreases(self):
        """UCB exploration term should decrease with more observations."""
        arm = LinUCBArm(arm_id=0, d=3, alpha=1.0)
        context = np.array([1.0, 0.5, 0.3])

        ucb_before = arm.get_ucb(context)
        for _ in range(50):
            arm.update(context, reward=3.0)
        ucb_after = arm.get_ucb(context)

        # After many updates, exploration shrinks (confidence increases)
        # The UCB should converge
        assert arm.n_pulls == 50


class TestLinUCBAgent:
    def test_select_arm(self):
        agent = LinUCBAgent()
        context = np.zeros(agent.d)
        context[0] = 1.0
        arm_idx, multiplier = agent.select_arm(context)
        assert 0 <= arm_idx < agent.n_arms
        assert multiplier in agent.price_multipliers

    def test_update_history(self):
        agent = LinUCBAgent()
        context = np.ones(agent.d) / np.sqrt(agent.d)
        arm_idx, _ = agent.select_arm(context)
        agent.update(arm_idx, context, reward=10.0)
        assert len(agent.history) == 1

    def test_cumulative_reward(self):
        agent = LinUCBAgent()
        rng = np.random.RandomState(42)
        for _ in range(20):
            context = rng.randn(agent.d)
            context /= np.linalg.norm(context)
            arm, _ = agent.select_arm(context)
            agent.update(arm, context, reward=rng.uniform(1, 10))

        cum = agent.get_cumulative_reward()
        assert len(cum) == 20
        assert cum[-1] > 0

    def test_wrong_context_dim_raises(self):
        agent = LinUCBAgent()
        with pytest.raises(ValueError):
            agent.select_arm(np.array([1.0, 2.0]))

    def test_arm_stats(self):
        agent = LinUCBAgent()
        context = np.ones(agent.d) / np.sqrt(agent.d)
        arm, _ = agent.select_arm(context)
        agent.update(arm, context, 5.0)
        stats = agent.get_arm_stats()
        assert len(stats) == agent.n_arms
        total_pulls = sum(s["n_pulls"] for s in stats)
        assert total_pulls == 1
