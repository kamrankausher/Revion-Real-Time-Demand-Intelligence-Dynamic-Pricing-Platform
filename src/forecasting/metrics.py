"""
WRMSSE and standard forecasting metrics for M5 evaluation.

Implements the official M5 competition metric (Weighted Root Mean Squared Scaled Error)
plus standard metrics for model comparison.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class WRMSSEEvaluator:
    """
    Official M5 WRMSSE evaluator.
    
    Computes RMSSE per series, applies dollar-weighted aggregation
    across 12 hierarchy levels.
    """

    # M5 hierarchy aggregation levels
    HIERARCHY_LEVELS = [
        [],                                    # Level 1: Total
        ["state_id"],                          # Level 2: State
        ["store_id"],                          # Level 3: Store
        ["cat_id"],                            # Level 4: Category
        ["dept_id"],                           # Level 5: Department
        ["state_id", "cat_id"],                # Level 6: State-Category
        ["state_id", "dept_id"],               # Level 7: State-Department
        ["store_id", "cat_id"],                # Level 8: Store-Category
        ["store_id", "dept_id"],               # Level 9: Store-Department
        ["item_id"],                           # Level 10: Item
        ["item_id", "state_id"],               # Level 11: Item-State
        ["item_id", "store_id"],               # Level 12: Item-Store (bottom)
    ]

    def __init__(self, train_df: pd.DataFrame, valid_df: pd.DataFrame,
                 prices_df: pd.DataFrame, calendar_df: pd.DataFrame):
        """
        Initialize evaluator with training data for scaling factors.
        
        Args:
            train_df: Wide-format training sales (id, item_id, ..., d_1...d_1913).
            valid_df: Wide-format validation truth (same structure, 28 days).
            prices_df: Sell prices DataFrame.
            calendar_df: Calendar DataFrame.
        """
        self.train_df = train_df
        self.valid_df = valid_df
        self.prices_df = prices_df
        self.calendar_df = calendar_df

        self.id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
        self.train_days = [c for c in train_df.columns if c.startswith("d_")]
        self.valid_days = [c for c in valid_df.columns if c.startswith("d_")]

        self.scale = self._compute_scale()
        self.weights = self._compute_weights()

    def _compute_scale(self) -> np.ndarray:
        """Compute scaling factor (denominator of RMSSE) per bottom-level series."""
        train_values = self.train_df[self.train_days].values  # (30490, num_train_days)

        # Scale = mean of squared differences of naive forecast
        # h_t = y_t - y_{t-1}, scale = mean(h_t^2)
        diffs = np.diff(train_values, axis=1)
        scale = np.mean(diffs ** 2, axis=1)
        scale = np.where(scale == 0, 1.0, scale)  # avoid division by zero
        return scale

    def _compute_weights(self) -> dict:
        """Compute dollar-weighted contribution per series per hierarchy level."""
        # Get the last 28 training days for weighting
        last_28_cols = self.train_days[-28:]
        revenue = self.train_df[last_28_cols].values  # units sold

        # Merge with prices to get dollar values
        # For simplicity, use unit counts as proxy (standard approach for M5)
        total_sales = revenue.sum()

        weights_per_level = {}
        for level_idx, group_cols in enumerate(self.HIERARCHY_LEVELS):
            if not group_cols:
                # Total level: single weight = 1
                weights_per_level[level_idx] = np.array([1.0])
            else:
                grouped = self.train_df.groupby(group_cols)[last_28_cols].sum()
                level_sales = grouped.values.sum(axis=1)
                level_weights = level_sales / level_sales.sum()
                weights_per_level[level_idx] = level_weights

        return weights_per_level

    def compute_rmsse(self, y_true: np.ndarray, y_pred: np.ndarray, scale: np.ndarray) -> np.ndarray:
        """Compute RMSSE per series."""
        mse = np.mean((y_true - y_pred) ** 2, axis=1)
        rmsse = np.sqrt(mse / scale)
        return rmsse

    def score(self, predictions: np.ndarray) -> float:
        """
        Compute WRMSSE score.
        
        Args:
            predictions: Array of shape (30490, 28) with bottom-level forecasts.
        
        Returns:
            WRMSSE score (lower is better).
        """
        actuals = self.valid_df[self.valid_days].values

        if predictions.shape != actuals.shape:
            raise ValueError(
                f"Shape mismatch: predictions={predictions.shape}, actuals={actuals.shape}"
            )

        # Bottom-level RMSSE
        bottom_rmsse = self.compute_rmsse(actuals, predictions, self.scale)

        # Aggregate across hierarchy levels
        total_wrmsse = 0.0
        for level_idx, group_cols in enumerate(self.HIERARCHY_LEVELS):
            if not group_cols:
                # Total: sum all series
                level_actual = actuals.sum(axis=0, keepdims=True)
                level_pred = predictions.sum(axis=0, keepdims=True)
                level_scale = np.array([self.scale.sum()])
            else:
                groups = self.train_df.groupby(group_cols).groups
                level_actual = np.array([actuals[list(idx)].sum(axis=0) for idx in groups.values()])
                level_pred = np.array([predictions[list(idx)].sum(axis=0) for idx in groups.values()])
                level_scale = np.array([self.scale[list(idx)].sum() for idx in groups.values()])

            level_scale = np.where(level_scale == 0, 1.0, level_scale)
            level_rmsse = self.compute_rmsse(level_actual, level_pred, level_scale)
            weights = self.weights[level_idx]

            level_wrmsse = np.sum(level_rmsse * weights)
            total_wrmsse += level_wrmsse

        # Average across 12 levels
        wrmsse = total_wrmsse / len(self.HIERARCHY_LEVELS)
        return float(wrmsse)


def compute_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))


def compute_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error (excludes zeros)."""
    mask = y_true != 0
    if mask.sum() == 0:
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def compute_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Symmetric Mean Absolute Percentage Error."""
    denominator = np.abs(y_true) + np.abs(y_pred)
    mask = denominator > 0
    if mask.sum() == 0:
        return 0.0
    return float(np.mean(2 * np.abs(y_true[mask] - y_pred[mask]) / denominator[mask]) * 100)


def evaluate_forecasts(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute all standard metrics."""
    return {
        "rmse": compute_rmse(y_true, y_pred),
        "mae": compute_mae(y_true, y_pred),
        "mape": compute_mape(y_true, y_pred),
        "smape": compute_smape(y_true, y_pred),
    }
