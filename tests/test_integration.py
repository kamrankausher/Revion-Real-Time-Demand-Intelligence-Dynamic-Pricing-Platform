"""
Integration tests: config validation, cross-module imports, and E2E pipeline.
"""

import importlib
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from src.config import (
    PROJECT_ROOT, DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR,
    FEATURE_STORE_DIR, MODELS_DIR, MLFLOW_DIR,
    m5, features, lgbm, tft, pricing, anomaly, api, mlflow_cfg,
)


# ──────────────────────────── Config Validation ──────────────────────────────

class TestConfigIntegrity:
    """Verify all configuration objects are valid and consistent."""

    def test_project_root_exists(self):
        assert PROJECT_ROOT.exists()

    def test_all_directories_exist(self):
        for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, FEATURE_STORE_DIR, MODELS_DIR]:
            assert d.exists(), f"Directory missing: {d}"

    def test_lgbm_params_valid(self):
        assert 0 < lgbm.learning_rate <= 1.0
        assert lgbm.num_leaves > 0
        assert lgbm.n_estimators > 0
        assert lgbm.subsample > 0

    def test_tft_params_valid(self):
        assert tft.hidden_size > 0
        assert tft.max_prediction_length > 0
        assert 0 < tft.dropout < 1

    def test_pricing_params_valid(self):
        assert pricing.alpha > 0
        assert pricing.context_dim > 0
        assert pricing.num_arms == len(pricing.price_multipliers)
        assert all(m > 0 for m in pricing.price_multipliers)

    def test_anomaly_params_valid(self):
        assert 0 < anomaly.contamination < 0.5
        assert anomaly.n_estimators > 0
        assert anomaly.stl_period > 0

    def test_m5_hierarchy(self):
        assert m5.num_stores == 10
        assert m5.num_items == 3049
        assert m5.forecast_horizon == 28
        total_stores = sum(len(v) for v in m5.stores_per_state.values())
        assert total_stores == m5.num_stores

    def test_lgbm_to_dict(self):
        d = lgbm.to_dict()
        assert isinstance(d, dict)
        assert "objective" in d
        assert d["objective"] == "tweedie"


# ──────────────────────────── Import Validation ──────────────────────────────

class TestModuleImports:
    """Verify all project modules import without errors."""

    @pytest.mark.parametrize("module_path", [
        "src.config",
        "src.data_pipeline.ingestion",
        "src.data_pipeline.feature_engineering",
        "src.data_pipeline.feature_store",
        "src.forecasting.metrics",
        "src.forecasting.lightgbm_model",
        "src.forecasting.reconciliation",
        "src.pricing.linucb_bandit",
        "src.pricing.demand_model",
        "src.pricing.simulator",
        "src.anomaly.stl_detector",
        "src.anomaly.isolation_forest",
        "src.anomaly.explainer",
        "src.causal.did_analysis",
        "src.api.app",
    ])
    def test_import_module(self, module_path):
        mod = importlib.import_module(module_path)
        assert mod is not None


# ──────────────────────────── Docker / CI Validation ──────────────────────────

class TestInfrastructureFiles:
    """Verify Docker and CI/CD files are present and valid."""

    def test_dockerfile_exists(self):
        p = PROJECT_ROOT / "docker" / "Dockerfile"
        assert p.exists(), f"Missing: {p}"

    def test_docker_compose_exists(self):
        p = PROJECT_ROOT / "docker" / "docker-compose.yml"
        assert p.exists(), f"Missing: {p}"

    def test_ci_workflow_exists(self):
        p = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        assert p.exists(), f"Missing: {p}"

    def test_requirements_exists(self):
        p = PROJECT_ROOT / "requirements.txt"
        assert p.exists()
        content = p.read_text()
        assert "fastapi" in content.lower()
        assert "pytest" in content.lower()

    def test_gitignore_exists(self):
        p = PROJECT_ROOT / ".gitignore"
        assert p.exists()

    def test_dockerfile_has_healthcheck(self):
        content = (PROJECT_ROOT / "docker" / "Dockerfile").read_text()
        assert "HEALTHCHECK" in content

    def test_ci_has_pytest_step(self):
        content = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text()
        assert "pytest" in content
        assert "push" in content
