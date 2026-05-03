"""
M5 Dataset Ingestion Module.

Handles loading, validating, and transforming the Walmart M5 dataset
from wide format to analysis-ready long format with calendar and price joins.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, m5

logger = logging.getLogger(__name__)


class M5DataLoader:
    """
    Production-grade loader for the M5 Forecasting dataset.
    
    Handles:
    - Raw CSV ingestion with schema validation
    - Wide-to-long format transformation
    - Calendar and price data joins
    - Data quality checks
    """

    def __init__(self, raw_dir: Optional[Path] = None):
        self.raw_dir = raw_dir or RAW_DATA_DIR
        self._validate_files_exist()

    def _validate_files_exist(self) -> None:
        """Verify all required M5 files are present."""
        required_files = [
            m5.sales_train_file,
            m5.calendar_file,
            m5.sell_prices_file,
        ]
        missing = [f for f in required_files if not (self.raw_dir / f).exists()]
        if missing:
            raise FileNotFoundError(
                f"Missing M5 dataset files in {self.raw_dir}: {missing}. "
                f"Download from: https://www.kaggle.com/competitions/m5-forecasting-accuracy/data"
            )

    def load_sales(self, use_eval: bool = False) -> pd.DataFrame:
        """
        Load sales training data.
        
        Args:
            use_eval: If True, load evaluation file (d_1 to d_1941).
                      If False, load validation file (d_1 to d_1913).
        
        Returns:
            DataFrame with item metadata + daily sales columns.
        """
        filename = m5.sales_train_eval_file if use_eval else m5.sales_train_file
        filepath = self.raw_dir / filename

        # Fall back to validation file if eval not available
        if use_eval and not filepath.exists():
            logger.warning(
                f"{filename} not found, falling back to {m5.sales_train_file}"
            )
            filepath = self.raw_dir / m5.sales_train_file

        logger.info(f"Loading sales data from {filepath}")
        df = pd.read_csv(filepath)

        # Validate schema
        expected_id_cols = {"id", "item_id", "dept_id", "cat_id", "store_id", "state_id"}
        actual_cols = set(df.columns)
        if not expected_id_cols.issubset(actual_cols):
            missing_cols = expected_id_cols - actual_cols
            raise ValueError(f"Sales data missing expected columns: {missing_cols}")

        logger.info(
            f"Sales data loaded: {df.shape[0]} series, "
            f"{len([c for c in df.columns if c.startswith('d_')])} days"
        )
        return df

    def load_calendar(self) -> pd.DataFrame:
        """
        Load calendar data with date, event, and SNAP information.
        
        Returns:
            DataFrame with calendar features indexed by day number.
        """
        filepath = self.raw_dir / m5.calendar_file
        logger.info(f"Loading calendar from {filepath}")

        df = pd.read_csv(filepath, parse_dates=["date"])

        # Validate expected columns
        expected_cols = {"date", "wm_yr_wk", "weekday", "wday", "month", "year", "d"}
        if not expected_cols.issubset(set(df.columns)):
            raise ValueError(f"Calendar missing expected columns")

        # Fill NaN events with empty string
        event_cols = [c for c in df.columns if c.startswith("event_")]
        df[event_cols] = df[event_cols].fillna("")

        logger.info(f"Calendar loaded: {len(df)} days, {df['date'].min()} to {df['date'].max()}")
        return df

    def load_prices(self) -> pd.DataFrame:
        """
        Load weekly sell prices per store-item.
        
        Returns:
            DataFrame with store_id, item_id, wm_yr_wk, sell_price columns.
        """
        filepath = self.raw_dir / m5.sell_prices_file
        logger.info(f"Loading sell prices from {filepath}")

        df = pd.read_csv(filepath)

        expected_cols = {"store_id", "item_id", "wm_yr_wk", "sell_price"}
        if not expected_cols.issubset(set(df.columns)):
            raise ValueError(f"Prices missing expected columns")

        logger.info(
            f"Prices loaded: {len(df)} records, "
            f"{df['item_id'].nunique()} items, {df['store_id'].nunique()} stores"
        )
        return df

    def melt_sales_to_long(self, sales_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert wide-format sales to long format.
        
        Transforms from:
            id | item_id | ... | d_1 | d_2 | ... | d_1913
        To:
            id | item_id | ... | d | sales
        
        Args:
            sales_df: Wide-format sales DataFrame.
        
        Returns:
            Long-format DataFrame with one row per item-store-day.
        """
        id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
        day_cols = [c for c in sales_df.columns if c.startswith("d_")]

        logger.info(f"Melting {len(day_cols)} day columns to long format...")

        df_long = sales_df.melt(
            id_vars=id_cols,
            value_vars=day_cols,
            var_name="d",
            value_name="sales",
        )

        # Extract day number for efficient joins
        df_long["d_num"] = df_long["d"].str.extract(r"d_(\d+)").astype(np.int32)

        logger.info(f"Long format created: {len(df_long):,} rows")
        return df_long

    def merge_all(
        self,
        sales_long: pd.DataFrame,
        calendar: pd.DataFrame,
        prices: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Merge sales with calendar and price data.
        
        Args:
            sales_long: Long-format sales data.
            calendar: Calendar DataFrame.
            prices: Sell prices DataFrame.
        
        Returns:
            Fully merged DataFrame ready for feature engineering.
        """
        logger.info("Merging sales with calendar...")
        df = sales_long.merge(calendar, on="d", how="left", validate="many_to_one")

        logger.info("Merging with sell prices...")
        df = df.merge(
            prices,
            on=["store_id", "item_id", "wm_yr_wk"],
            how="left",
        )

        # Handle missing prices (items not yet available)
        price_null_pct = df["sell_price"].isna().mean() * 100
        logger.info(f"Price coverage: {100 - price_null_pct:.1f}% (missing: {price_null_pct:.1f}%)")

        # Sort for time-series operations
        df = df.sort_values(["id", "date"]).reset_index(drop=True)

        logger.info(f"Merged dataset: {len(df):,} rows, {len(df.columns)} columns")
        return df

    def load_and_merge(self, use_eval: bool = False) -> pd.DataFrame:
        """
        Full ingestion pipeline: load all files, transform, and merge.
        
        Args:
            use_eval: Whether to use evaluation dataset.
        
        Returns:
            Fully merged long-format DataFrame.
        """
        sales = self.load_sales(use_eval=use_eval)
        calendar = self.load_calendar()
        prices = self.load_prices()

        sales_long = self.melt_sales_to_long(sales)
        merged = self.merge_all(sales_long, calendar, prices)

        return merged

    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """
        Generate a summary of the loaded dataset for validation.
        
        Args:
            df: Merged DataFrame.
        
        Returns:
            Dictionary with dataset statistics.
        """
        return {
            "total_rows": len(df),
            "num_items": df["item_id"].nunique(),
            "num_stores": df["store_id"].nunique(),
            "num_series": df["id"].nunique(),
            "date_range": (str(df["date"].min()), str(df["date"].max())),
            "num_days": df["date"].nunique(),
            "categories": df["cat_id"].unique().tolist(),
            "departments": df["dept_id"].unique().tolist(),
            "states": df["state_id"].unique().tolist(),
            "avg_daily_sales": float(df["sales"].mean()),
            "zero_sales_pct": float((df["sales"] == 0).mean() * 100),
            "price_null_pct": float(df["sell_price"].isna().mean() * 100),
            "memory_mb": float(df.memory_usage(deep=True).sum() / 1e6),
        }


def download_m5_dataset(target_dir: Optional[Path] = None) -> None:
    """
    Download M5 dataset using Kaggle CLI.
    
    Requires:
        - kaggle package installed
        - ~/.kaggle/kaggle.json credentials file
    
    Args:
        target_dir: Directory to download files into.
    """
    target_dir = target_dir or RAW_DATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        import subprocess
        logger.info("Downloading M5 dataset from Kaggle...")
        subprocess.run(
            [
                "kaggle", "competitions", "download",
                "-c", "m5-forecasting-accuracy",
                "-p", str(target_dir),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        # Unzip
        import zipfile
        zip_path = target_dir / "m5-forecasting-accuracy.zip"
        if zip_path.exists():
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(target_dir)
            zip_path.unlink()
            logger.info(f"M5 dataset extracted to {target_dir}")

    except FileNotFoundError:
        logger.error(
            "kaggle CLI not found. Install with: pip install kaggle\n"
            "Then configure: https://github.com/Kaggle/kaggle-api#api-credentials"
        )
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Kaggle download failed: {e.stderr}")
        raise
