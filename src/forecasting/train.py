"""
Training Orchestrator.

Manages end-to-end training pipeline: data prep, model training,
evaluation, comparison, and MLflow experiment tracking.
"""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd
import mlflow

from src.config import mlflow_cfg, MODELS_DIR
from src.forecasting.lightgbm_model import LightGBMForecaster
from src.forecasting.tft_model import TFTForecaster
from src.forecasting.reconciliation import HierarchicalReconciler
from src.forecasting.metrics import evaluate_forecasts

logger = logging.getLogger(__name__)


class TrainingOrchestrator:
    """Orchestrates training of all forecasting models with MLflow tracking."""

    def __init__(self):
        self.lgbm = LightGBMForecaster()
        self.tft = TFTForecaster()
        self.reconciler = HierarchicalReconciler()
        self._setup_mlflow()

    def _setup_mlflow(self):
        """Configure MLflow tracking."""
        mlflow.set_tracking_uri(mlflow_cfg.tracking_uri)
        mlflow.set_experiment(mlflow_cfg.experiment_name)
        logger.info(f"MLflow tracking: {mlflow_cfg.tracking_uri}")

    def train_lightgbm(self, df: pd.DataFrame,
                       train_end_day: int = 1885) -> Dict:
        """Train LightGBM with MLflow logging."""
        with mlflow.start_run(run_name="lightgbm_forecaster"):
            train, valid, test = self.lgbm.prepare_data(df, train_end_day=train_end_day)
            results = self.lgbm.train(train, valid)

            # Log to MLflow
            mlflow.log_params({
                "model": "lightgbm",
                "objective": self.lgbm.config.objective,
                "num_leaves": self.lgbm.config.num_leaves,
                "learning_rate": self.lgbm.config.learning_rate,
                "n_estimators": self.lgbm.config.n_estimators,
                "train_samples": len(train),
                "valid_samples": len(valid),
            })
            for metric_name, value in results["valid_metrics"].items():
                mlflow.log_metric(f"valid_{metric_name}", value)
            for metric_name, value in results["train_metrics"].items():
                mlflow.log_metric(f"train_{metric_name}", value)

            # Save model
            model_path = self.lgbm.save()
            mlflow.log_artifact(str(model_path))

            # Log feature importance
            fi = self.lgbm.get_top_features(20)
            fi.to_csv(MODELS_DIR / "lgbm_feature_importance.csv", index=False)
            mlflow.log_artifact(str(MODELS_DIR / "lgbm_feature_importance.csv"))

            logger.info("LightGBM training complete")
            return results

    def train_tft(self, df: pd.DataFrame) -> Dict:
        """Train TFT with MLflow logging."""
        with mlflow.start_run(run_name="tft_forecaster"):
            train_ds, val_ds = self.tft.prepare_dataset(df)
            results = self.tft.train(train_ds, val_ds)

            mlflow.log_params({
                "model": "tft",
                "hidden_size": self.tft.config.hidden_size,
                "attention_heads": self.tft.config.attention_head_size,
                "dropout": self.tft.config.dropout,
                "max_encoder_length": self.tft.config.max_encoder_length,
                "batch_size": self.tft.config.batch_size,
            })
            mlflow.log_metric("best_val_loss", results["best_val_loss"])
            mlflow.log_metric("epochs_trained", results["epochs_trained"])

            model_path = self.tft.save()
            mlflow.log_artifact(str(model_path))

            logger.info("TFT training complete")
            return results

    def compare_models(self, df: pd.DataFrame, actuals: np.ndarray) -> pd.DataFrame:
        """Compare LightGBM and TFT on the same validation set."""
        results = []

        # LightGBM predictions
        lgbm_preds = self.lgbm.predict(df)
        lgbm_metrics = evaluate_forecasts(actuals, lgbm_preds)
        lgbm_metrics["model"] = "LightGBM"
        results.append(lgbm_metrics)

        # TFT predictions (if trained)
        if self.tft.model is not None:
            tft_preds = self.tft.predict(df)
            tft_metrics = evaluate_forecasts(actuals, tft_preds.flatten()[:len(actuals)])
            tft_metrics["model"] = "TFT"
            results.append(tft_metrics)

        comparison = pd.DataFrame(results)
        logger.info(f"\nModel Comparison:\n{comparison.to_string()}")
        return comparison

    def run_full_pipeline(self, df: pd.DataFrame) -> Dict:
        """Run complete training pipeline."""
        logger.info("=" * 60)
        logger.info("Starting full training pipeline...")
        logger.info("=" * 60)

        results = {}

        # 1. Build hierarchy map
        self.reconciler.build_hierarchy_map(df)

        # 2. Train LightGBM
        logger.info("\n--- Training LightGBM ---")
        results["lightgbm"] = self.train_lightgbm(df)

        # 3. Train TFT (optional, resource-intensive)
        try:
            logger.info("\n--- Training TFT ---")
            results["tft"] = self.train_tft(df)
        except Exception as e:
            logger.warning(f"TFT training skipped: {e}")
            results["tft"] = {"error": str(e)}

        logger.info("Training pipeline complete")
        return results
