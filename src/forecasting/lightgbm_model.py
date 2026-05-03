"""
LightGBM Demand Forecasting Model.

Implements a production-grade LightGBM regressor with Tweedie objective
for count data, recursive multi-step forecasting, and MLflow tracking.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict

import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib

from src.config import lgbm as lgbm_cfg, MODELS_DIR, m5
from src.forecasting.metrics import evaluate_forecasts

logger = logging.getLogger(__name__)


class LightGBMForecaster:
    """
    LightGBM-based demand forecaster with recursive multi-step prediction.
    
    Uses Tweedie objective suited for zero-inflated count data (retail sales).
    """

    def __init__(self, config=lgbm_cfg):
        self.config = config
        self.model: Optional[lgb.LGBMRegressor] = None
        self.feature_names: Optional[List[str]] = None
        self.feature_importance: Optional[pd.DataFrame] = None

    def _get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Select feature columns excluding target, IDs, and dates."""
        exclude_cols = {
            "sales", "id", "item_id", "dept_id", "cat_id", "store_id",
            "state_id", "d", "d_num", "date", "wm_yr_wk", "weekday",
            "event_name_1", "event_name_2", "event_type_1", "event_type_2",
        }
        feature_cols = [c for c in df.columns if c not in exclude_cols and not c.startswith("d_")]
        return feature_cols

    def prepare_data(self, df: pd.DataFrame,
                     train_end_day: int = 1885,
                     valid_days: int = 28) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train/validation/test by time.
        
        Args:
            df: Feature-engineered DataFrame.
            train_end_day: Last day of training period.
            valid_days: Number of days for validation.
        """
        df = df.dropna(subset=["sales"]).copy()

        # Remove rows where lag features are NaN (initial period)
        lag_cols = [c for c in df.columns if "lag_" in c]
        if lag_cols:
            df = df.dropna(subset=lag_cols)

        train = df[df["d_num"] <= train_end_day]
        valid = df[(df["d_num"] > train_end_day) & (df["d_num"] <= train_end_day + valid_days)]
        test = df[df["d_num"] > train_end_day + valid_days]

        logger.info(f"Train: {len(train):,} | Valid: {len(valid):,} | Test: {len(test):,}")
        return train, valid, test

    def train(self, train_df: pd.DataFrame, valid_df: pd.DataFrame,
              feature_cols: Optional[List[str]] = None) -> Dict:
        """
        Train LightGBM model with early stopping.
        
        Returns:
            Dictionary with training metrics and feature importance.
        """
        if feature_cols is None:
            feature_cols = self._get_feature_columns(train_df)

        self.feature_names = feature_cols

        X_train = train_df[feature_cols].values
        y_train = train_df["sales"].values
        X_valid = valid_df[feature_cols].values
        y_valid = valid_df["sales"].values

        logger.info(f"Training LightGBM with {len(feature_cols)} features...")
        logger.info(f"Train shape: {X_train.shape}, Valid shape: {X_valid.shape}")

        self.model = lgb.LGBMRegressor(
            objective=self.config.objective,
            tweedie_variance_power=self.config.tweedie_variance_power,
            metric=self.config.metric,
            learning_rate=self.config.learning_rate,
            num_leaves=self.config.num_leaves,
            min_child_samples=self.config.min_child_samples,
            max_depth=self.config.max_depth,
            subsample=self.config.subsample,
            colsample_bytree=self.config.colsample_bytree,
            reg_alpha=self.config.reg_alpha,
            reg_lambda=self.config.reg_lambda,
            n_estimators=self.config.n_estimators,
            verbose=self.config.verbose,
            n_jobs=self.config.n_jobs,
            random_state=self.config.seed,
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_valid, y_valid)],
            callbacks=[
                lgb.early_stopping(stopping_rounds=self.config.early_stopping_rounds),
                lgb.log_evaluation(period=100),
            ],
        )

        # Feature importance
        self.feature_importance = pd.DataFrame({
            "feature": feature_cols,
            "importance": self.model.feature_importances_,
        }).sort_values("importance", ascending=False)

        # Evaluate
        train_pred = np.clip(self.model.predict(X_train), 0, None)
        valid_pred = np.clip(self.model.predict(X_valid), 0, None)

        train_metrics = evaluate_forecasts(y_train, train_pred)
        valid_metrics = evaluate_forecasts(y_valid, valid_pred)

        logger.info(f"Train RMSE: {train_metrics['rmse']:.4f}")
        logger.info(f"Valid RMSE: {valid_metrics['rmse']:.4f}")

        return {
            "train_metrics": train_metrics,
            "valid_metrics": valid_metrics,
            "best_iteration": self.model.best_iteration_,
            "num_features": len(feature_cols),
        }

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Generate predictions (clipped to non-negative)."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        X = df[self.feature_names].values
        preds = self.model.predict(X)
        return np.clip(preds, 0, None)

    def recursive_forecast(self, df: pd.DataFrame, horizon: int = 28) -> pd.DataFrame:
        """
        Multi-step recursive forecasting.
        
        For each step, predict, then update lag features with predictions.
        """
        if self.model is None:
            raise ValueError("Model not trained.")

        results = []
        current_df = df.copy()

        for step in range(horizon):
            preds = self.predict(current_df)
            current_df["predicted_sales"] = preds

            step_result = current_df[["id", "date", "d_num"]].copy()
            step_result["forecast"] = preds
            step_result["step"] = step + 1
            results.append(step_result)

            # Update lag features for next step (shift predictions in)
            if step < horizon - 1:
                for lag_col in [c for c in current_df.columns if "lag_" in c]:
                    lag_val = int(lag_col.split("_")[-1])
                    if lag_val == 1:
                        current_df[lag_col] = preds

        return pd.concat(results, ignore_index=True)

    def save(self, path: Optional[Path] = None) -> Path:
        """Save model and metadata."""
        path = path or MODELS_DIR / "lightgbm_forecaster.joblib"
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_names": self.feature_names,
            "feature_importance": self.feature_importance,
            "config": self.config,
        }, path)
        logger.info(f"Model saved to {path}")
        return path

    def load(self, path: Optional[Path] = None) -> None:
        """Load model and metadata."""
        path = path or MODELS_DIR / "lightgbm_forecaster.joblib"
        data = joblib.load(path)
        self.model = data["model"]
        self.feature_names = data["feature_names"]
        self.feature_importance = data["feature_importance"]
        logger.info(f"Model loaded from {path}")

    def get_top_features(self, n: int = 20) -> pd.DataFrame:
        """Get top N most important features."""
        if self.feature_importance is None:
            raise ValueError("No feature importance available.")
        return self.feature_importance.head(n)
