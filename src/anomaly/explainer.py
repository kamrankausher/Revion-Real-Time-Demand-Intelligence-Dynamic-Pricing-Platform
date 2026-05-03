"""
SHAP-based Anomaly Explainer.

Generates human-readable explanations for detected anomalies
using SHAP values from the Isolation Forest model.
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.config import anomaly as anomaly_cfg

logger = logging.getLogger(__name__)


class AnomalyExplainer:
    """Explains anomalies using SHAP values and feature contribution analysis."""

    def __init__(self, config=anomaly_cfg):
        self.config = config

    def explain_with_shap(self, model, X: np.ndarray,
                          feature_names: List[str],
                          max_samples: int = 1000) -> Optional[np.ndarray]:
        """
        Compute SHAP values for the Isolation Forest.
        
        Falls back to permutation-based explanation if TreeExplainer fails.
        """
        try:
            import shap

            if X.shape[0] > max_samples:
                idx = np.random.choice(X.shape[0], max_samples, replace=False)
                X_sample = X[idx]
            else:
                X_sample = X

            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
            logger.info(f"SHAP values computed: {shap_values.shape}")
            return shap_values

        except Exception as e:
            logger.warning(f"SHAP TreeExplainer failed: {e}. Using feature importance fallback.")
            return None

    def get_top_contributors(self, shap_values: np.ndarray,
                              feature_names: List[str],
                              anomaly_idx: int, top_k: int = 5) -> List[Dict]:
        """Get top contributing features for a specific anomaly."""
        if shap_values is None:
            return []

        sv = shap_values[anomaly_idx]
        abs_sv = np.abs(sv)
        top_indices = abs_sv.argsort()[-top_k:][::-1]

        contributors = []
        for idx in top_indices:
            contributors.append({
                "feature": feature_names[idx],
                "shap_value": float(sv[idx]),
                "abs_importance": float(abs_sv[idx]),
                "direction": "increased_risk" if sv[idx] > 0 else "decreased_risk",
            })
        return contributors

    def explain_anomaly_batch(self, model, X: np.ndarray,
                               anomaly_mask: np.ndarray,
                               feature_names: List[str]) -> pd.DataFrame:
        """
        Generate explanations for all detected anomalies.
        
        Returns DataFrame with top contributing features per anomaly.
        """
        shap_values = self.explain_with_shap(model, X, feature_names)

        if shap_values is None:
            # Fallback: use feature values relative to population
            return self._explain_by_deviation(X, anomaly_mask, feature_names)

        anomaly_indices = np.where(anomaly_mask)[0]
        explanations = []

        for idx in anomaly_indices:
            # Map back to SHAP index if subsampled
            if idx < len(shap_values):
                contributors = self.get_top_contributors(shap_values, feature_names, idx)
                explanations.append({
                    "anomaly_idx": int(idx),
                    "top_features": contributors,
                    "explanation": self._generate_text(contributors),
                })

        return pd.DataFrame(explanations)

    def _explain_by_deviation(self, X: np.ndarray, anomaly_mask: np.ndarray,
                               feature_names: List[str]) -> pd.DataFrame:
        """Fallback explanation using z-scores from population statistics."""
        pop_mean = X.mean(axis=0)
        pop_std = X.std(axis=0) + 1e-8

        anomaly_indices = np.where(anomaly_mask)[0]
        explanations = []

        for idx in anomaly_indices:
            z_scores = (X[idx] - pop_mean) / pop_std
            abs_z = np.abs(z_scores)
            top_k = min(5, len(feature_names))
            top_indices = abs_z.argsort()[-top_k:][::-1]

            contributors = [
                {
                    "feature": feature_names[i],
                    "z_score": float(z_scores[i]),
                    "direction": "unusually_high" if z_scores[i] > 0 else "unusually_low",
                }
                for i in top_indices
            ]
            explanations.append({
                "anomaly_idx": int(idx),
                "top_features": contributors,
                "explanation": self._generate_text_from_zscore(contributors),
            })

        return pd.DataFrame(explanations)

    @staticmethod
    def _generate_text(contributors: List[Dict]) -> str:
        """Generate human-readable explanation from SHAP contributors."""
        if not contributors:
            return "No explanation available."

        parts = []
        for c in contributors[:3]:
            feature = c["feature"].replace("_", " ")
            direction = "high" if c.get("direction", "") == "increased_risk" else "low"
            parts.append(f"{feature} is {direction}")

        return "Anomaly driven by: " + "; ".join(parts) + "."

    @staticmethod
    def _generate_text_from_zscore(contributors: List[Dict]) -> str:
        """Generate explanation from z-score analysis."""
        if not contributors:
            return "No explanation available."

        parts = []
        for c in contributors[:3]:
            feature = c["feature"].replace("_", " ")
            direction = c.get("direction", "unusual")
            z = abs(c.get("z_score", 0))
            parts.append(f"{feature} is {direction} ({z:.1f}σ)")

        return "Anomaly driven by: " + "; ".join(parts) + "."
