"""
Temporal Fusion Transformer (TFT) Model.

Uses pytorch-forecasting for state-of-the-art attention-based
time series forecasting with built-in interpretability.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Tuple

import numpy as np
import pandas as pd
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, LearningRateMonitor
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss

from src.config import tft as tft_cfg, MODELS_DIR

logger = logging.getLogger(__name__)


class TFTForecaster:
    """
    TFT-based demand forecaster with interpretability outputs.
    
    Wraps pytorch-forecasting TemporalFusionTransformer with
    production-ready data preparation and training pipeline.
    """

    def __init__(self, config=tft_cfg):
        self.config = config
        self.model: Optional[TemporalFusionTransformer] = None
        self.training_dataset: Optional[TimeSeriesDataSet] = None
        self.trainer: Optional[pl.Trainer] = None

    def prepare_dataset(self, df: pd.DataFrame,
                        training_cutoff: Optional[int] = None) -> Tuple[TimeSeriesDataSet, TimeSeriesDataSet]:
        """
        Create TimeSeriesDataSet objects for training and validation.
        
        Args:
            df: Feature-engineered DataFrame with time_idx column.
            training_cutoff: time_idx value to split train/val.
        
        Returns:
            Tuple of (training_dataset, validation_dataset).
        """
        if training_cutoff is None:
            training_cutoff = df["time_idx"].max() - self.config.max_prediction_length

        # Ensure required columns exist
        required = ["time_idx", "sales", "id"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Filter to series with enough history
        series_lengths = df.groupby("id")["time_idx"].count()
        valid_series = series_lengths[
            series_lengths >= self.config.max_encoder_length + self.config.max_prediction_length
        ].index
        df = df[df["id"].isin(valid_series)].copy()
        logger.info(f"Using {len(valid_series)} series with sufficient history")

        # Prepare known and unknown reals
        time_varying_known = [c for c in self.config.time_varying_known_reals if c in df.columns]
        time_varying_unknown = [c for c in self.config.time_varying_unknown_reals if c in df.columns]
        static_cats = [c for c in self.config.static_categoricals
                       if f"{c}_encoded" in df.columns]

        # Use encoded categoricals
        static_cat_cols = [f"{c}_encoded" for c in static_cats]
        for col in static_cat_cols:
            df[col] = df[col].astype(str)

        # Build training dataset
        self.training_dataset = TimeSeriesDataSet(
            df[df["time_idx"] <= training_cutoff],
            time_idx="time_idx",
            target="sales",
            group_ids=["id"],
            min_encoder_length=self.config.max_encoder_length // 2,
            max_encoder_length=self.config.max_encoder_length,
            min_prediction_length=1,
            max_prediction_length=self.config.max_prediction_length,
            static_categoricals=static_cat_cols,
            time_varying_known_reals=time_varying_known,
            time_varying_unknown_reals=time_varying_unknown,
            target_normalizer=GroupNormalizer(groups=["id"], transformation="softplus"),
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,
        )

        # Validation dataset from training definition
        validation = TimeSeriesDataSet.from_dataset(
            self.training_dataset,
            df,
            predict=True,
            stop_randomization=True,
        )

        logger.info(
            f"Training dataset: {len(self.training_dataset)} samples, "
            f"Validation: {len(validation)} samples"
        )
        return self.training_dataset, validation

    def train(self, training_ds: TimeSeriesDataSet,
              validation_ds: TimeSeriesDataSet) -> Dict:
        """
        Train TFT model with PyTorch Lightning.
        
        Returns:
            Dictionary with training results.
        """
        train_loader = training_ds.to_dataloader(
            train=True, batch_size=self.config.batch_size, num_workers=0
        )
        val_loader = validation_ds.to_dataloader(
            train=False, batch_size=self.config.batch_size * 2, num_workers=0
        )

        # Configure callbacks
        early_stop = EarlyStopping(
            monitor="val_loss",
            patience=self.config.early_stop_patience,
            verbose=True,
            mode="min",
        )
        lr_monitor = LearningRateMonitor()

        self.trainer = pl.Trainer(
            max_epochs=self.config.max_epochs,
            accelerator=self.config.accelerator,
            devices=self.config.devices,
            gradient_clip_val=self.config.gradient_clip_val,
            callbacks=[early_stop, lr_monitor],
            enable_progress_bar=True,
            enable_model_summary=True,
            deterministic=True,
        )

        # Build model
        self.model = TemporalFusionTransformer.from_dataset(
            training_ds,
            learning_rate=self.config.learning_rate,
            hidden_size=self.config.hidden_size,
            attention_head_size=self.config.attention_head_size,
            dropout=self.config.dropout,
            hidden_continuous_size=self.config.hidden_continuous_size,
            output_size=7,  # 7 quantiles
            loss=QuantileLoss(),
            reduce_on_plateau_patience=self.config.reduce_lr_patience,
            log_interval=10,
        )

        logger.info(f"TFT model parameters: {self.model.size() / 1e3:.1f}K")

        # Train
        self.trainer.fit(self.model, train_dataloaders=train_loader, val_dataloaders=val_loader)

        best_model_path = self.trainer.checkpoint_callback.best_model_path
        logger.info(f"Best model checkpoint: {best_model_path}")

        return {
            "best_val_loss": float(self.trainer.callback_metrics.get("val_loss", 0)),
            "epochs_trained": self.trainer.current_epoch,
            "best_model_path": best_model_path,
        }

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Generate point forecasts (median quantile)."""
        if self.model is None:
            raise ValueError("Model not trained.")

        dataset = TimeSeriesDataSet.from_dataset(
            self.training_dataset, df, predict=True, stop_randomization=True
        )
        loader = dataset.to_dataloader(train=False, batch_size=256, num_workers=0)

        predictions = self.model.predict(loader, mode="prediction")
        return predictions.numpy()

    def get_interpretation(self, df: pd.DataFrame) -> Dict:
        """Extract attention weights and variable importance."""
        if self.model is None:
            raise ValueError("Model not trained.")

        dataset = TimeSeriesDataSet.from_dataset(
            self.training_dataset, df, predict=True, stop_randomization=True
        )
        loader = dataset.to_dataloader(train=False, batch_size=64, num_workers=0)

        interpretation = self.model.interpret_output(
            self.model.predict(loader, mode="raw", return_x=True),
            reduction="mean",
        )
        return interpretation

    def save(self, path: Optional[Path] = None) -> Path:
        """Save model checkpoint."""
        path = path or MODELS_DIR / "tft_forecaster.ckpt"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.trainer.save_checkpoint(str(path))
        logger.info(f"TFT model saved to {path}")
        return path

    def load(self, path: Optional[Path] = None) -> None:
        """Load model from checkpoint."""
        path = path or MODELS_DIR / "tft_forecaster.ckpt"
        self.model = TemporalFusionTransformer.load_from_checkpoint(str(path))
        logger.info(f"TFT model loaded from {path}")
