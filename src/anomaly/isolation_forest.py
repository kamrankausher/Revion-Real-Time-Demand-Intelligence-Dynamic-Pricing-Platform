"""
Isolation Forest Anomaly Detector.

Uses feature-based Isolation Forest for unsupervised anomaly detection
on demand time series with multiple contextual signals.
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest as SklearnIsolationForest
import joblib

from src.config import anomaly as anomaly_cfg, MODELS_DIR

logger = logging.getLogger(__name__)


class IsolationForestDetector:
    """Isolation Forest anomaly detector with feature engineering."""

    FEATURE_COLS = [
        "sales", "sell_price", "sales_lag_7", "sales_lag_14",
        "sales_roll_7_mean", "sales_roll_7_std",
        "sales_roll_28_mean", "sales_roll_28_std",
        "price_change", "promotion_flag",
        "day_of_week", "month", "is_weekend",
    ]

    def __init__(self, config=anomaly_cfg):
        self.config = config
        self.model: Optional[SklearnIsolationForest] = None
        self.feature_cols: List[str] = []

    def _select_features(self, df: pd.DataFrame) -> List[str]:
        """Select available features from the predefined list."""
        available = [c for c in self.FEATURE_COLS if c in df.columns]
        if not available:
            raise ValueError("No anomaly detection features available in DataFrame")
        return available

    def fit(self, df: pd.DataFrame) -> None:
        """Fit Isolation Forest on training data."""
        self.feature_cols = self._select_features(df)
        X = df[self.feature_cols].fillna(0).values

        logger.info(f"Fitting Isolation Forest on {X.shape[0]} samples, {X.shape[1]} features")

        self.model = SklearnIsolationForest(
            contamination=self.config.contamination,
            n_estimators=self.config.n_estimators,
            max_samples=self.config.max_samples,
            random_state=self.config.random_state,
            n_jobs=-1,
        )
        self.model.fit(X)
        logger.info("Isolation Forest fitted")

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in new data.
        
        Returns DataFrame with anomaly scores and labels.
        -1 = anomaly, 1 = normal
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        X = df[self.feature_cols].fillna(0).values

        predictions = self.model.predict(X)
        scores = self.model.decision_function(X)

        result = df[["id", "date"] if "id" in df.columns else ["date"]].copy()
        result["anomaly_label"] = predictions
        result["anomaly_score"] = scores
        result["is_anomaly"] = predictions == -1

        n_anomalies = result["is_anomaly"].sum()
        logger.info(f"Isolation Forest: {n_anomalies} anomalies ({n_anomalies/len(df)*100:.1f}%)")
        return result

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit and predict in one step."""
        self.fit(df)
        return self.predict(df)

    def save(self, path=None):
        """Save fitted model."""
        path = path or MODELS_DIR / "isolation_forest.joblib"
        joblib.dump({"model": self.model, "feature_cols": self.feature_cols}, path)

    def load(self, path=None):
        """Load fitted model."""
        path = path or MODELS_DIR / "isolation_forest.joblib"
        data = joblib.load(path)
        self.model = data["model"]
        self.feature_cols = data["feature_cols"]
