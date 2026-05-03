"""
Exploratory Data Analysis Module.

Generates summary statistics and diagnostic plots for the M5 dataset.
All plots are saved to files for reproducibility.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)
PLOTS_DIR = PROJECT_ROOT / "notebooks" / "eda_plots"


class EDAAnalyzer:
    """Generates comprehensive EDA reports for M5 data."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or PLOTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def sales_distribution(self, df: pd.DataFrame) -> dict:
        """Analyze overall sales distribution."""
        stats = {
            "mean": float(df["sales"].mean()),
            "median": float(df["sales"].median()),
            "std": float(df["sales"].std()),
            "zero_pct": float((df["sales"] == 0).mean() * 100),
            "max": float(df["sales"].max()),
            "skewness": float(df["sales"].skew()),
            "kurtosis": float(df["sales"].kurtosis()),
        }
        logger.info(f"Sales stats: mean={stats['mean']:.2f}, zero_pct={stats['zero_pct']:.1f}%")

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].hist(df["sales"].clip(upper=20), bins=21, edgecolor="black", alpha=0.7)
        axes[0].set_title("Sales Distribution (clipped at 20)")
        axes[0].set_xlabel("Daily Sales")
        axes[1].hist(np.log1p(df["sales"]), bins=50, edgecolor="black", alpha=0.7)
        axes[1].set_title("Log(1+Sales) Distribution")
        plt.tight_layout()
        plt.savefig(self.output_dir / "sales_distribution.png", dpi=150)
        plt.close()
        return stats

    def seasonality_patterns(self, df: pd.DataFrame) -> None:
        """Plot sales seasonality by day-of-week, month, and year."""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        if "day_of_week" in df.columns:
            df.groupby("day_of_week")["sales"].mean().plot(kind="bar", ax=axes[0])
            axes[0].set_title("Avg Sales by Day of Week")

        if "month" in df.columns:
            df.groupby("month")["sales"].mean().plot(kind="bar", ax=axes[1])
            axes[1].set_title("Avg Sales by Month")

        if "year" in df.columns:
            df.groupby("year")["sales"].mean().plot(kind="bar", ax=axes[2])
            axes[2].set_title("Avg Sales by Year")

        plt.tight_layout()
        plt.savefig(self.output_dir / "seasonality_patterns.png", dpi=150)
        plt.close()

    def category_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sales by category and department."""
        cat_stats = df.groupby("cat_id")["sales"].agg(["mean", "std", "sum", "count"])
        cat_stats.to_csv(self.output_dir / "category_stats.csv")

        fig, ax = plt.subplots(figsize=(10, 5))
        df.groupby("cat_id")["sales"].mean().plot(kind="bar", ax=ax)
        ax.set_title("Average Daily Sales by Category")
        plt.tight_layout()
        plt.savefig(self.output_dir / "category_analysis.png", dpi=150)
        plt.close()
        return cat_stats

    def store_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sales by store and state."""
        store_stats = df.groupby("store_id")["sales"].agg(["mean", "std", "sum"])

        fig, ax = plt.subplots(figsize=(12, 5))
        store_stats["mean"].plot(kind="bar", ax=ax)
        ax.set_title("Average Daily Sales by Store")
        plt.tight_layout()
        plt.savefig(self.output_dir / "store_analysis.png", dpi=150)
        plt.close()
        return store_stats

    def price_analysis(self, df: pd.DataFrame) -> None:
        """Analyze price distributions and promotion patterns."""
        if "sell_price" not in df.columns:
            return
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        df["sell_price"].dropna().hist(bins=50, ax=axes[0], alpha=0.7)
        axes[0].set_title("Price Distribution")
        if "promotion_flag" in df.columns:
            promo_rate = df.groupby("cat_id")["promotion_flag"].mean()
            promo_rate.plot(kind="bar", ax=axes[1])
            axes[1].set_title("Promotion Rate by Category")
        plt.tight_layout()
        plt.savefig(self.output_dir / "price_analysis.png", dpi=150)
        plt.close()

    def missing_data_audit(self, df: pd.DataFrame) -> pd.DataFrame:
        """Audit missing values across all columns."""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        audit = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
        audit = audit[audit["missing_count"] > 0].sort_values("missing_pct", ascending=False)
        audit.to_csv(self.output_dir / "missing_data_audit.csv")
        logger.info(f"Missing data audit: {len(audit)} columns with missing values")
        return audit

    def run_full_eda(self, df: pd.DataFrame) -> dict:
        """Run complete EDA pipeline."""
        logger.info("Running full EDA...")
        results = {
            "sales_stats": self.sales_distribution(df),
            "category_stats": self.category_analysis(df).to_dict(),
            "store_stats": self.store_analysis(df).to_dict(),
            "missing_audit": self.missing_data_audit(df).to_dict(),
        }
        self.seasonality_patterns(df)
        self.price_analysis(df)
        logger.info(f"EDA complete. Plots saved to {self.output_dir}")
        return results
