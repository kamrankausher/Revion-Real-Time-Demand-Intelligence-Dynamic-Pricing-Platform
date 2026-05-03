"""
Feature Store Module.

Manages persistence of engineered features as partitioned Parquet files
for efficient loading and reproducibility.
"""

import logging
from pathlib import Path
from typing import Optional, List

import pandas as pd

from src.config import FEATURE_STORE_DIR

logger = logging.getLogger(__name__)


class FeatureStore:
    """Parquet-based feature store with partitioned storage."""

    def __init__(self, store_dir: Optional[Path] = None):
        self.store_dir = store_dir or FEATURE_STORE_DIR
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def save_features(self, df: pd.DataFrame, name: str = "features",
                      partition_col: Optional[str] = "store_id") -> Path:
        """Save features as partitioned Parquet files."""
        save_path = self.store_dir / name
        save_path.mkdir(parents=True, exist_ok=True)

        if partition_col and partition_col in df.columns:
            logger.info(f"Saving features partitioned by '{partition_col}' to {save_path}")
            df.to_parquet(save_path, partition_cols=[partition_col], engine="pyarrow", index=False)
        else:
            file_path = save_path / "data.parquet"
            logger.info(f"Saving features to {file_path}")
            df.to_parquet(file_path, engine="pyarrow", index=False)

        size_mb = sum(f.stat().st_size for f in save_path.rglob("*.parquet")) / 1e6
        logger.info(f"Saved {len(df):,} rows ({size_mb:.1f} MB)")
        return save_path

    def load_features(self, name: str = "features",
                      filters: Optional[List] = None,
                      columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load features from Parquet with optional filtering."""
        load_path = self.store_dir / name
        if not load_path.exists():
            raise FileNotFoundError(f"Feature set '{name}' not found at {load_path}")

        logger.info(f"Loading features from {load_path}")
        df = pd.read_parquet(load_path, filters=filters, columns=columns, engine="pyarrow")
        logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
        return df

    def list_feature_sets(self) -> List[str]:
        """List all available feature sets."""
        return [p.name for p in self.store_dir.iterdir() if p.is_dir()]

    def get_feature_info(self, name: str = "features") -> dict:
        """Get metadata about a feature set."""
        load_path = self.store_dir / name
        if not load_path.exists():
            raise FileNotFoundError(f"Feature set '{name}' not found")
        parquet_files = list(load_path.rglob("*.parquet"))
        total_size = sum(f.stat().st_size for f in parquet_files) / 1e6
        sample = pd.read_parquet(parquet_files[0], engine="pyarrow")
        return {
            "name": name, "num_files": len(parquet_files),
            "total_size_mb": round(total_size, 2), "num_columns": len(sample.columns),
            "columns": sample.columns.tolist(), "dtypes": sample.dtypes.astype(str).to_dict(),
        }
