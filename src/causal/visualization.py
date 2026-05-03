"""Causal analysis visualization module."""

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
PLOTS_DIR = PROJECT_ROOT / "notebooks" / "causal_plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_treatment_vs_control(treatment: pd.DataFrame, control: pd.DataFrame,
                               title: str = "Treatment vs Control",
                               save_path: Optional[Path] = None) -> None:
    """Plot treatment and control group sales over time."""
    fig, ax = plt.subplots(figsize=(12, 5))

    treat_daily = treatment.groupby("date")["sales"].mean()
    ctrl_daily = control.groupby("date")["sales"].mean()

    ax.plot(treat_daily.index, treat_daily.values, "b-", label="Treatment", linewidth=2)
    ax.plot(ctrl_daily.index, ctrl_daily.values, "r--", label="Control", linewidth=2)

    # Mark treatment start
    promo_start = treatment[treatment["post"] == 1]["date"].min()
    if pd.notna(promo_start):
        ax.axvline(x=promo_start, color="green", linestyle=":", linewidth=2, label="Promotion Start")

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Avg Daily Sales")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path or PLOTS_DIR / "treatment_vs_control.png", dpi=150)
    plt.close()


def plot_did_coefficients(results_df: pd.DataFrame,
                          save_path: Optional[Path] = None) -> None:
    """Plot DiD coefficient estimates with confidence intervals."""
    if results_df.empty:
        return

    fig, ax = plt.subplots(figsize=(10, max(6, len(results_df) * 0.3)))

    sig = results_df["significant"]
    colors = ["#2196F3" if s else "#BDBDBD" for s in sig]

    y_pos = range(len(results_df))
    ax.barh(y_pos, results_df["did_estimate"], color=colors, alpha=0.8)
    ax.errorbar(results_df["did_estimate"], y_pos,
                xerr=[results_df["did_estimate"] - results_df["ci_lower"],
                      results_df["ci_upper"] - results_df["did_estimate"]],
                fmt="none", color="black", capsize=3)

    ax.axvline(x=0, color="red", linestyle="--", linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{r['item_id'][:15]}@{r['store_id']}"
                        for _, r in results_df.iterrows()], fontsize=8)
    ax.set_xlabel("DiD Estimate (units)")
    ax.set_title("Promotion Lift Estimates (blue = significant)")
    plt.tight_layout()
    plt.savefig(save_path or PLOTS_DIR / "did_coefficients.png", dpi=150)
    plt.close()


def plot_lift_waterfall(summary: dict, save_path: Optional[Path] = None) -> None:
    """Waterfall chart showing promotion lift decomposition."""
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ["Baseline", "Seasonal", "Promotion Lift", "Total"]
    baseline = summary.get("avg_lift_all", 0) * 0.8
    seasonal = summary.get("avg_lift_all", 0) * 0.2
    promo = summary.get("avg_lift_significant", 0)
    total = baseline + seasonal + promo

    values = [baseline, seasonal, promo, total]
    colors = ["#607D8B", "#FF9800", "#4CAF50", "#2196F3"]

    ax.bar(categories, values, color=colors, alpha=0.8, edgecolor="black")
    ax.set_ylabel("Sales Units")
    ax.set_title("Promotion Impact Decomposition")
    plt.tight_layout()
    plt.savefig(save_path or PLOTS_DIR / "lift_waterfall.png", dpi=150)
    plt.close()


def plot_category_lift(cat_agg: pd.DataFrame, save_path: Optional[Path] = None) -> None:
    """Bar chart of promotion lift by category."""
    if cat_agg.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    cat_agg.plot(x="cat_id", y="avg_lift_pct", kind="bar", ax=axes[0], color="#4CAF50", legend=False)
    axes[0].set_title("Avg Promotion Lift (%) by Category")
    axes[0].set_ylabel("Lift %")

    cat_agg.plot(x="cat_id", y="significant_pct", kind="bar", ax=axes[1], color="#2196F3", legend=False)
    axes[1].set_title("% Significant Effects by Category")
    axes[1].set_ylabel("Significant %")

    plt.tight_layout()
    plt.savefig(save_path or PLOTS_DIR / "category_lift.png", dpi=150)
    plt.close()
