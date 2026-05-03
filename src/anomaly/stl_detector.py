"""
STL Decomposition-based Anomaly Detector.

Uses seasonal-trend decomposition to isolate residuals
and flag anomalies based on z-score thresholds.
"""

import logging
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

from src.config import anomaly as anomaly_cfg

logger = logging.getLogger(__name__)


class STLAnomalyDetector:
    """Anomaly detection via STL residual analysis."""

    def __init__(self, config=anomaly_cfg):
        self.config = config

    def decompose(self, series: pd.Series, period: Optional[int] = None) -> Dict[str, pd.Series]:
        """Run STL decomposition on a time series."""
        period = period or self.config.stl_period

        if len(series) < period * 2:
            logger.warning(f"Series too short ({len(series)}) for period {period}")
            return {"trend": series, "seasonal": pd.Series(0, index=series.index),
                    "resid": pd.Series(0, index=series.index)}

        stl = STL(series, period=period, robust=self.config.stl_robust)
        result = stl.fit()

        return {
            "trend": result.trend,
            "seasonal": result.seasonal,
            "resid": result.resid,
        }

    def detect(self, series: pd.Series, period: Optional[int] = None,
               threshold: Optional[float] = None) -> pd.DataFrame:
        """
        Detect anomalies using STL residual z-scores.
        
        Args:
            series: Time series of demand values.
            period: Seasonal period.
            threshold: Z-score threshold for anomaly.
        
        Returns:
            DataFrame with decomposition and anomaly flags.
        """
        threshold = threshold or self.config.residual_zscore_threshold

        components = self.decompose(series, period)

        resid = components["resid"]
        resid_mean = resid.mean()
        resid_std = resid.std()

        if resid_std == 0:
            z_scores = pd.Series(0, index=series.index)
        else:
            z_scores = (resid - resid_mean) / resid_std

        result = pd.DataFrame({
            "value": series,
            "trend": components["trend"],
            "seasonal": components["seasonal"],
            "residual": resid,
            "z_score": z_scores,
            "is_anomaly": np.abs(z_scores) > threshold,
        })

        n_anomalies = result["is_anomaly"].sum()
        logger.info(f"STL detected {n_anomalies} anomalies ({n_anomalies/len(series)*100:.1f}%)")
        return result

    def detect_batch(self, df: pd.DataFrame, group_col: str = "id",
                     value_col: str = "sales", date_col: str = "date") -> pd.DataFrame:
        """Detect anomalies across multiple time series."""
        results = []
        groups = df.groupby(group_col)
        total = len(groups)

        for i, (group_id, gdf) in enumerate(groups):
            if i % 1000 == 0:
                logger.info(f"Processing series {i}/{total}")

            gdf = gdf.sort_values(date_col)
            series = gdf.set_index(date_col)[value_col]

            if len(series) < self.config.stl_period * 2:
                continue

            detected = self.detect(series)
            detected["id"] = group_id
            detected["date"] = detected.index
            results.append(detected.reset_index(drop=True))

        if not results:
            return pd.DataFrame()

        return pd.concat(results, ignore_index=True)
