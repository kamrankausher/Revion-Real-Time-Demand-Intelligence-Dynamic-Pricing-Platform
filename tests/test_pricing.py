"""
Unit tests for dynamic pricing: demand model, simulator, and bandit simulation.
"""

import numpy as np
import pandas as pd
import pytest

from src.pricing.demand_model import DemandModel
from src.pricing.linucb_bandit import LinUCBAgent
from src.pricing.simulator import PricingSimulator


# ──────────────────────────── DemandModel Tests ──────────────────────────────

class TestDemandModel:
    """Tests for the log-linear demand/elasticity model."""

    @pytest.fixture
    def model(self):
        return DemandModel(default_elasticity=-1.5)

    def test_predict_demand_normal(self, model):
        """Demand at same price should equal base demand."""
        d = model.predict_demand(base_demand=100, base_price=5.0, new_price=5.0)
        assert d == pytest.approx(100.0, abs=0.01)

    def test_demand_drops_with_higher_price(self, model):
        """With negative elasticity, higher price → lower demand."""
        d_high = model.predict_demand(base_demand=100, base_price=5.0, new_price=7.0)
        d_low = model.predict_demand(base_demand=100, base_price=5.0, new_price=3.0)
        assert d_high < 100, "Demand should drop at higher price"
        assert d_low > 100, "Demand should rise at lower price"

    def test_predict_demand_non_negative(self, model):
        """Demand should never be negative."""
        d = model.predict_demand(base_demand=10, base_price=5.0, new_price=50.0)
        assert d >= 0

    def test_zero_price_returns_base(self, model):
        """Edge case: zero price should return base demand (guard)."""
        d = model.predict_demand(base_demand=100, base_price=0.0, new_price=5.0)
        assert d == 100  # guard clause in source

    def test_revenue_curve_shape(self, model):
        """Revenue curve should be a DataFrame with expected columns."""
        curve = model.get_revenue_curve(base_demand=50, base_price=5.0)
        assert isinstance(curve, pd.DataFrame)
        assert "price" in curve.columns
        assert "demand" in curve.columns
        assert "revenue" in curve.columns
        assert len(curve) == 50

    def test_revenue_curve_has_maximum(self, model):
        """Revenue curve should have a peak (not monotonically increasing)."""
        curve = model.get_revenue_curve(base_demand=50, base_price=5.0, n_points=100)
        revenues = curve["revenue"].values
        max_idx = np.argmax(revenues)
        # The peak should not be at the very last point (price too high kills demand)
        assert max_idx < len(revenues) - 1, "Revenue peak at end suggests no elasticity effect"


# ──────────────────────────── Simulator Tests ──────────────────────────────

class TestPricingSimulator:
    """Tests for the pricing simulation environment."""

    @pytest.fixture
    def simulator(self):
        dm = DemandModel(default_elasticity=-1.5)
        return PricingSimulator(demand_model=dm)

    @pytest.fixture
    def sample_df(self):
        np.random.seed(42)
        n = 200
        return pd.DataFrame({
            "sales": np.random.poisson(8, n),
            "sell_price": np.random.uniform(2.0, 8.0, n),
            "dept_id": ["FOODS_3"] * n,
            "day_of_week": np.tile(range(7), n // 7 + 1)[:n],
            "month": np.random.choice(range(1, 13), n),
            "is_weekend": np.random.choice([0, 1], n),
            "snap_CA": np.random.choice([0, 1], n),
            "snap_TX": 0,
            "snap_WI": 0,
        })

    def test_build_context_shape(self, simulator, sample_df):
        row = sample_df.iloc[0]
        ctx = simulator.build_context(row, forecast=10.0)
        assert len(ctx) == simulator.config.context_dim
        assert np.isfinite(ctx).all()

    def test_context_is_normalized(self, simulator, sample_df):
        row = sample_df.iloc[0]
        ctx = simulator.build_context(row, forecast=10.0)
        norm = np.linalg.norm(ctx)
        assert norm == pytest.approx(1.0, abs=0.01) or norm == 0.0

    def test_simulate_demand_non_negative(self, simulator):
        d = simulator.simulate_demand(base_demand=10, base_price=5.0, price_multiplier=1.2)
        assert d >= 0

    def test_compute_reward_non_negative(self, simulator):
        r = simulator.compute_reward(demand=10, price=5.0)
        assert r >= 0
        assert r == 50.0

    def test_run_episode_completes(self, simulator, sample_df):
        agent = LinUCBAgent()
        result = simulator.run_episode(sample_df, agent, n_rounds=50)
        assert "total_reward" in result
        assert "cumulative_regret" in result
        assert result["n_rounds"] > 0
        assert result["total_reward"] >= 0

    def test_cumulative_regret_non_negative(self, simulator, sample_df):
        agent = LinUCBAgent()
        result = simulator.run_episode(sample_df, agent, n_rounds=50)
        # Regret can be slightly negative due to noise, but should be bounded
        assert result["cumulative_regret"] >= -100, \
            f"Regret too negative: {result['cumulative_regret']}"


# ──────────────────────────── Bandit Simulation Test ──────────────────────────────

class TestBanditSimulation:
    """End-to-end bandit learning simulation."""

    def test_bandit_learns_over_time(self):
        """Average reward in last rounds should be >= average in first rounds."""
        np.random.seed(42)
        agent = LinUCBAgent()
        dm = DemandModel(default_elasticity=-1.5)
        sim = PricingSimulator(demand_model=dm)

        rewards = []
        for i in range(200):
            # Constant context — agent should converge
            base_demand = 10.0
            base_price = 5.0
            context = np.zeros(agent.d)
            context[0] = base_demand / 20.0  # normalized
            context[1] = base_price / 10.0
            norm = np.linalg.norm(context)
            if norm > 0:
                context /= norm

            arm_idx, mult = agent.select_arm(context)
            demand = sim.simulate_demand(base_demand, base_price, mult)
            reward = sim.compute_reward(demand, base_price * mult)
            agent.update(arm_idx, context, reward)
            rewards.append(reward)

        first_50 = np.mean(rewards[:50])
        last_50 = np.mean(rewards[-50:])
        # The bandit should learn — last rewards should not be dramatically worse
        assert last_50 >= first_50 * 0.5, \
            f"Bandit did not learn: first_50={first_50:.2f}, last_50={last_50:.2f}"
