"""
Unit tests for anomaly detection modules.
"""

import numpy as np
import pandas as pd
import pytest
from src.anomaly.stl_detector import STLAnomalyDetector
from src.anomaly.isolation_forest import IsolationForestDetector
from src.anomaly.explainer import AnomalyExplainer


class TestSTLAnomalyDetector:
    @pytest.fixture
    def detector(self):
        return STLAnomalyDetector()

    @pytest.fixture
    def sample_series(self):
        np.random.seed(42)
        n = 365
        t = np.arange(n)
        seasonal = 5 * np.sin(2 * np.pi * t / 7)
        trend = 0.01 * t
        noise = np.random.normal(0, 0.5, n)
        values = 10 + seasonal + trend + noise
        # Inject anomalies
        values[50] = 40
        values[200] = -5
        dates = pd.date_range("2020-01-01", periods=n, freq="D")
        return pd.Series(values, index=dates)

    def test_decompose(self, detector, sample_series):
        result = detector.decompose(sample_series)
        assert "trend" in result
        assert "seasonal" in result
        assert "resid" in result
        assert len(result["trend"]) == len(sample_series)

    def test_detect_finds_anomalies(self, detector, sample_series):
        result = detector.detect(sample_series, threshold=3.0)
        assert "is_anomaly" in result.columns
        assert result["is_anomaly"].sum() > 0

    def test_short_series(self, detector):
        short = pd.Series([1, 2, 3, 4, 5])
        result = detector.decompose(short)
        assert len(result["trend"]) == 5


class TestIsolationForestDetector:
    @pytest.fixture
    def detector(self):
        return IsolationForestDetector()

    @pytest.fixture
    def sample_df(self):
        np.random.seed(42)
        n = 500
        df = pd.DataFrame({
            "id": ["item_1"] * n,
            "date": pd.date_range("2020-01-01", periods=n),
            "sales": np.random.poisson(5, n),
            "sell_price": np.random.uniform(1, 10, n),
            "sales_lag_7": np.random.poisson(5, n),
            "sales_roll_7_mean": np.random.uniform(3, 7, n),
            "day_of_week": np.tile(range(7), n // 7 + 1)[:n],
        })
        # Inject anomaly
        df.loc[100, "sales"] = 100
        return df

    def test_fit_predict(self, detector, sample_df):
        result = detector.fit_predict(sample_df)
        assert "is_anomaly" in result.columns
        assert result["is_anomaly"].sum() > 0

    def test_no_features_raises(self, detector):
        df = pd.DataFrame({"x": [1, 2, 3]})
        with pytest.raises(ValueError):
            detector.fit(df)


class TestAnomalyExplainer:
    def test_generate_text(self):
        contributors = [
            {"feature": "sales_lag_7", "direction": "increased_risk"},
            {"feature": "sell_price", "direction": "decreased_risk"},
        ]
        text = AnomalyExplainer._generate_text(contributors)
        assert "sales lag 7" in text
        assert "Anomaly driven by" in text

    def test_empty_contributors(self):
        text = AnomalyExplainer._generate_text([])
        assert text == "No explanation available."
