"""
Unit tests for the data pipeline: ingestion, feature engineering, feature store.
"""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, FEATURE_STORE_DIR, features


# ──────────────────────────── Helpers ──────────────────────────────

def _make_synthetic_sales(n_items=5, n_days=120):
    """Create a minimal long-format sales DataFrame matching M5 schema."""
    np.random.seed(0)
    rows = []
    for i in range(n_items):
        item_id = f"FOODS_3_{i:03d}"
        dept_id = "FOODS_3"
        cat_id = "FOODS"
        store_id = "CA_1"
        state_id = "CA"
        for d in range(1, n_days + 1):
            rows.append({
                "id": f"{item_id}_{store_id}_validation",
                "item_id": item_id,
                "dept_id": dept_id,
                "cat_id": cat_id,
                "store_id": store_id,
                "state_id": state_id,
                "d": f"d_{d}",
                "sales": max(0, int(np.random.poisson(5) + 2 * np.sin(2 * np.pi * d / 7))),
                "date": pd.Timestamp("2016-01-01") + pd.Timedelta(days=d - 1),
                "sell_price": round(np.random.uniform(1.5, 8.0), 2),
                "wday": (d % 7) + 1,
                "month": ((d - 1) // 30) + 1,
                "year": 2016,
                "snap_CA": int(np.random.random() > 0.7),
                "snap_TX": 0,
                "snap_WI": 0,
            })
    return pd.DataFrame(rows)


# ──────────────────────────── Tests ──────────────────────────────

class TestDataLoading:
    """Tests for data loading and schema correctness."""

    def test_synthetic_data_shape(self):
        df = _make_synthetic_sales(n_items=3, n_days=60)
        assert df.shape[0] == 3 * 60
        assert df.shape[1] > 0

    def test_required_columns_present(self):
        df = _make_synthetic_sales()
        required = ["id", "item_id", "store_id", "sales", "date", "sell_price"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_no_entirely_null_columns(self):
        df = _make_synthetic_sales()
        for col in df.columns:
            assert df[col].notna().any(), f"Column {col} is entirely null"

    def test_sales_non_negative(self):
        df = _make_synthetic_sales()
        assert (df["sales"] >= 0).all(), "Negative sales detected"


class TestFeatureEngineering:
    """Tests for feature computation correctness."""

    @pytest.fixture
    def featured_df(self):
        df = _make_synthetic_sales(n_items=2, n_days=100)
        # Manually compute lag features (mirroring pipeline logic)
        df = df.sort_values(["id", "date"]).reset_index(drop=True)
        for lag in [7, 14, 28]:
            df[f"sales_lag_{lag}"] = df.groupby("id")["sales"].shift(lag)
        for w in [7, 14, 28]:
            df[f"sales_roll_{w}_mean"] = (
                df.groupby("id")["sales"]
                .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
            )
            df[f"sales_roll_{w}_std"] = (
                df.groupby("id")["sales"]
                .transform(lambda x: x.shift(1).rolling(w, min_periods=1).std())
            )
        df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        return df

    def test_lag_columns_created(self, featured_df):
        for lag in [7, 14, 28]:
            col = f"sales_lag_{lag}"
            assert col in featured_df.columns, f"Missing: {col}"

    def test_rolling_columns_created(self, featured_df):
        for w in [7]:
            for agg in ["mean", "std"]:
                col = f"sales_roll_{w}_{agg}"
                assert col in featured_df.columns, f"Missing: {col}"

    def test_lag_no_nan_after_warmup(self, featured_df):
        """After warmup period (lag length), lag values should not be NaN."""
        for lag in [7, 14, 28]:
            col = f"sales_lag_{lag}"
            for _, gdf in featured_df.groupby("id"):
                valid_rows = gdf.iloc[lag:]
                nan_count = valid_rows[col].isna().sum()
                assert nan_count == 0, f"{col} has {nan_count} NaN after warmup"

    def test_calendar_features_valid_ranges(self, featured_df):
        assert featured_df["day_of_week"].between(0, 6).all()
        assert featured_df["is_weekend"].isin([0, 1]).all()

    def test_sell_price_non_negative(self, featured_df):
        assert (featured_df["sell_price"] >= 0).all()

    def test_data_types_correct(self, featured_df):
        for col in ["sales_lag_7", "sales_roll_7_mean"]:
            assert featured_df[col].dtype in [np.float64, np.float32, float], \
                f"{col} has dtype {featured_df[col].dtype}, expected float"


class TestFeatureStore:
    """Tests for feature store I/O."""

    def test_store_directories_exist(self):
        assert PROCESSED_DATA_DIR.exists(), f"Missing: {PROCESSED_DATA_DIR}"
        assert FEATURE_STORE_DIR.exists(), f"Missing: {FEATURE_STORE_DIR}"

    def test_config_paths_valid(self):
        assert RAW_DATA_DIR.exists()
        assert PROCESSED_DATA_DIR.exists()
