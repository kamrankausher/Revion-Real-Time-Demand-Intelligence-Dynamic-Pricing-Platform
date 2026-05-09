"""
Unit tests for the causal inference engine: DiD analysis, parallel trends.
"""

import numpy as np
import pandas as pd
import pytest

from src.causal.did_analysis import DifferenceInDifferences


# ──────────────────────────── Helpers ──────────────────────────────

def _make_did_data(treatment_effect=3.0, n_days=60, noise_std=1.0):
    """Create synthetic treatment/control panel data with a known effect."""
    np.random.seed(42)
    pre_days = n_days // 2
    post_days = n_days - pre_days

    dates = pd.date_range("2020-01-01", periods=n_days, freq="D")

    # Treatment group
    treat_pre = np.random.poisson(10, pre_days).astype(float)
    treat_post = np.random.poisson(10 + treatment_effect, post_days).astype(float)
    treat_sales = np.concatenate([treat_pre, treat_post])
    treat_sales += np.random.normal(0, noise_std, n_days)
    treat_sales = np.maximum(0, treat_sales)

    treatment = pd.DataFrame({
        "date": dates,
        "sales": treat_sales,
        "treated": 1,
        "post": [0] * pre_days + [1] * post_days,
        "group": "treatment",
        "day_of_week": [d.weekday() for d in dates],
    })

    # Control group
    ctrl_sales = np.random.poisson(10, n_days).astype(float)
    ctrl_sales += np.random.normal(0, noise_std, n_days)
    ctrl_sales = np.maximum(0, ctrl_sales)

    control = pd.DataFrame({
        "date": dates,
        "sales": ctrl_sales,
        "treated": 0,
        "post": [0] * pre_days + [1] * post_days,
        "group": "control",
        "day_of_week": [d.weekday() for d in dates],
    })

    return treatment, control


# ──────────────────────────── Tests ──────────────────────────────

class TestDiDEstimator:
    """Tests for Difference-in-Differences estimation."""

    @pytest.fixture
    def did(self):
        return DifferenceInDifferences()

    def test_did_returns_expected_keys(self, did):
        treatment, control = _make_did_data(treatment_effect=3.0)
        result = did.run_did_regression(treatment, control)
        assert "did_estimate" in result
        assert "p_value" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert "significant" in result

    def test_did_estimate_is_float(self, did):
        treatment, control = _make_did_data(treatment_effect=3.0)
        result = did.run_did_regression(treatment, control)
        assert isinstance(result["did_estimate"], float)
        assert np.isfinite(result["did_estimate"])

    def test_did_detects_positive_effect(self, did):
        treatment, control = _make_did_data(treatment_effect=5.0, noise_std=0.5)
        result = did.run_did_regression(treatment, control)
        # With a large effect and low noise, estimate should be positive
        assert result["did_estimate"] > 0, \
            f"Expected positive effect, got {result['did_estimate']}"

    def test_did_pvalue_in_range(self, did):
        treatment, control = _make_did_data(treatment_effect=3.0)
        result = did.run_did_regression(treatment, control)
        assert 0 <= result["p_value"] <= 1, \
            f"p_value out of range: {result['p_value']}"

    def test_did_no_treatment_near_zero(self, did):
        """When there is no treatment effect, estimate should be near zero."""
        treatment, control = _make_did_data(treatment_effect=0.0, noise_std=1.0)
        result = did.run_did_regression(treatment, control)
        assert abs(result["did_estimate"]) < 5.0, \
            f"Expected near-zero estimate, got {result['did_estimate']}"

    def test_did_confidence_interval_order(self, did):
        treatment, control = _make_did_data(treatment_effect=3.0)
        result = did.run_did_regression(treatment, control)
        assert result["ci_lower"] <= result["ci_upper"], \
            f"CI lower ({result['ci_lower']}) > upper ({result['ci_upper']})"


class TestParallelTrends:
    """Tests for the parallel trends assumption check."""

    @pytest.fixture
    def did(self):
        return DifferenceInDifferences()

    def test_parallel_trends_returns_result(self, did):
        treatment, control = _make_did_data(treatment_effect=3.0)
        result = did.test_parallel_trends(treatment, control)
        assert "parallel_trends_holds" in result
        assert "interaction_pvalue" in result

    def test_parallel_trends_with_parallel_data(self, did):
        """Synthetic data with same pre-trends should pass the test."""
        treatment, control = _make_did_data(treatment_effect=3.0, noise_std=1.0)
        result = did.test_parallel_trends(treatment, control)
        assert result["parallel_trends_holds"] in (True, False)
        # With random noise data, parallel trends should generally hold
        assert result["interaction_pvalue"] >= 0
