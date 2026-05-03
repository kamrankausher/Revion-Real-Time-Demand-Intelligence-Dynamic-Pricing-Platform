"""
Feature Engineering Module.

Creates production-grade features for demand forecasting:
- Lag features (7, 14, 21, 28 days)
- Rolling window statistics (mean, std, min, max)
- Calendar & event features
- Price & promotion signals
- Categorical encodings
"""

import logging
from typing import List, Dict

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src.config import features as feat_cfg

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Stateful feature engineering pipeline for M5 time series data."""

    def __init__(self):
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self._is_fitted = False

    @staticmethod
    def add_lag_features(df, group_col="id", target_col="sales", lags=feat_cfg.lag_days):
        """Add lagged sales features per time series (shift prevents leakage)."""
        logger.info(f"Creating lag features: {lags}")
        for lag in lags:
            df[f"{target_col}_lag_{lag}"] = df.groupby(group_col)[target_col].shift(lag)
        return df

    @staticmethod
    def add_rolling_features(df, group_col="id", target_col="sales",
                             windows=feat_cfg.rolling_windows,
                             aggregations=feat_cfg.rolling_aggregations):
        """Add rolling window statistics computed on shift(1) to prevent leakage."""
        logger.info(f"Creating rolling features: windows={windows}")
        for window in windows:
            rolled = df.groupby(group_col)[target_col].shift(1).rolling(window=window, min_periods=1)
            for agg in aggregations:
                col = f"{target_col}_roll_{window}_{agg}"
                df[col] = getattr(rolled, agg)().reset_index(level=0, drop=True)
        return df

    @staticmethod
    def add_calendar_features(df):
        """Extract calendar features from the date column."""
        logger.info("Creating calendar features...")
        dt = pd.to_datetime(df["date"])
        df["day_of_week"] = dt.dt.dayofweek.astype(np.int8)
        df["day_of_month"] = dt.dt.day.astype(np.int8)
        df["day_of_year"] = dt.dt.dayofyear.astype(np.int16)
        df["week_of_year"] = dt.dt.isocalendar().week.astype(np.int8)
        df["month"] = dt.dt.month.astype(np.int8)
        df["quarter"] = dt.dt.quarter.astype(np.int8)
        df["year"] = dt.dt.year.astype(np.int16)
        df["is_weekend"] = (dt.dt.dayofweek >= 5).astype(np.int8)

        for col in [c for c in df.columns if c.startswith("event_name")]:
            df[f"has_{col}"] = (df[col] != "").astype(np.int8)

        for col in [c for c in df.columns if c.startswith("snap_")]:
            df[col] = df[col].astype(np.int8)

        return df

    @staticmethod
    def add_price_features(df, windows=feat_cfg.price_rolling_windows):
        """Create price-derived features: ratio, momentum, promotion flag."""
        logger.info("Creating price features...")
        if "sell_price" not in df.columns:
            return df

        cat_store_mean = df.groupby(["cat_id", "store_id"])["sell_price"].transform("mean")
        df["price_ratio_cat"] = np.where(cat_store_mean > 0, df["sell_price"] / cat_store_mean, 1.0)

        for window in windows:
            rolling_price = df.groupby("id")["sell_price"].transform(
                lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
            )
            df[f"price_momentum_{window}"] = np.where(rolling_price > 0, df["sell_price"] / rolling_price, 1.0)

        df["price_change"] = df.groupby("id")["sell_price"].diff().fillna(0)
        df["price_decreased"] = (df["price_change"] < 0).astype(np.int8)
        df["price_increased"] = (df["price_change"] > 0).astype(np.int8)

        rolling_avg = df.groupby("id")["sell_price"].transform(
            lambda x: x.shift(1).rolling(window=14, min_periods=1).mean()
        )
        df["promotion_flag"] = np.where(
            (rolling_avg > 0) & (df["sell_price"] < rolling_avg * 0.9), 1, 0
        ).astype(np.int8)

        return df

    def encode_categoricals(self, df, categorical_cols=feat_cfg.categorical_cols, fit=True):
        """Label-encode categorical columns with state management."""
        logger.info(f"Encoding categoricals: {categorical_cols}")
        for col in categorical_cols:
            if col not in df.columns:
                continue
            if fit:
                le = LabelEncoder()
                df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                le = self.label_encoders[col]
                known = set(le.classes_)
                df[f"{col}_encoded"] = df[col].astype(str).map(
                    lambda x, _le=le, _k=known: _le.transform([x])[0] if x in _k else -1
                )
        self._is_fitted = True
        return df

    @staticmethod
    def add_time_index(df):
        """Add monotonic time index per series (required for TFT)."""
        df["time_idx"] = df.groupby("id").cumcount()
        return df

    def run(self, df, fit_encoders=True):
        """Execute the full feature engineering pipeline."""
        logger.info("=" * 60)
        logger.info("Starting feature engineering pipeline...")
        initial_cols = len(df.columns)
        df = df.sort_values(["id", "date"]).reset_index(drop=True)

        df = self.add_calendar_features(df)
        df = self.add_price_features(df)
        df = self.add_lag_features(df)
        df = self.add_rolling_features(df)
        df = self.encode_categoricals(df, fit=fit_encoders)
        df = self.add_time_index(df)
        df = self._downcast_numerics(df)

        logger.info(f"Feature engineering complete: {initial_cols} -> {len(df.columns)} columns")
        return df

    @staticmethod
    def _downcast_numerics(df):
        """Reduce memory by downcasting numeric types."""
        for col in df.select_dtypes(include=["float64"]).columns:
            df[col] = df[col].astype(np.float32)
        for col in df.select_dtypes(include=["int64"]).columns:
            mn, mx = df[col].min(), df[col].max()
            if mn >= 0 and mx < 255:
                df[col] = df[col].astype(np.uint8)
            elif mn >= -128 and mx < 128:
                df[col] = df[col].astype(np.int8)
            elif mn >= -32768 and mx < 32768:
                df[col] = df[col].astype(np.int16)
            else:
                df[col] = df[col].astype(np.int32)
        return df

    def get_feature_names(self):
        """Return organized feature names by category."""
        return {
            "lag": [f"sales_lag_{l}" for l in feat_cfg.lag_days],
            "rolling": [f"sales_roll_{w}_{a}" for w in feat_cfg.rolling_windows for a in feat_cfg.rolling_aggregations],
            "calendar": ["day_of_week", "day_of_month", "day_of_year", "week_of_year", "month", "quarter", "year", "is_weekend"],
            "price": ["sell_price", "price_ratio_cat", "price_change", "price_decreased", "price_increased", "promotion_flag"],
            "categorical_encoded": [f"{c}_encoded" for c in feat_cfg.categorical_cols],
        }
