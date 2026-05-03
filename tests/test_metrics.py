"""
Unit tests for forecasting metrics.
"""

import numpy as np
import pytest
from src.forecasting.metrics import (
    compute_rmse as rmse, compute_mae as mae,
    compute_mape as mape, compute_smape as smape,
    evaluate_forecasts,
)


class TestMetrics:
    @pytest.fixture
    def sample_data(self):
        np.random.seed(42)
        actual = np.random.poisson(10, 100).astype(float)
        predicted = actual + np.random.normal(0, 1, 100)
        return actual, predicted

    def test_rmse(self, sample_data):
        actual, pred = sample_data
        val = rmse(actual, pred)
        assert val >= 0
        assert np.isfinite(val)

    def test_mae(self, sample_data):
        actual, pred = sample_data
        val = mae(actual, pred)
        assert val >= 0
        assert val <= rmse(actual, pred)  # MAE ≤ RMSE

    def test_mape(self, sample_data):
        actual, pred = sample_data
        val = mape(actual, pred)
        assert val >= 0

    def test_smape(self, sample_data):
        actual, pred = sample_data
        val = smape(actual, pred)
        assert 0 <= val <= 200  # SMAPE bounded [0, 200]

    def test_perfect_prediction(self):
        actual = np.array([1.0, 2.0, 3.0])
        assert rmse(actual, actual) == 0
        assert mae(actual, actual) == 0
        assert smape(actual, actual) == 0

    def test_evaluate_forecasts(self, sample_data):
        actual, pred = sample_data
        result = evaluate_forecasts(actual, pred)
        assert "rmse" in result
        assert "mae" in result
        assert "smape" in result
        assert all(np.isfinite(v) for v in result.values())
