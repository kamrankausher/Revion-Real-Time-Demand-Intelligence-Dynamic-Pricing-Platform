"""
Central configuration for the ⚡ Revion Platform.

All paths, hyperparameters, and constants are managed here.
Uses dataclasses for type safety and frozen=True for immutability.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional
import os


# ──────────────────────────── Base Paths ────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FEATURE_STORE_DIR = DATA_DIR / "feature_store"
MODELS_DIR = PROJECT_ROOT / "models"
MLFLOW_DIR = PROJECT_ROOT / "mlruns"

# Create directories on import
for _dir in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FEATURE_STORE_DIR, MODELS_DIR, MLFLOW_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)


# ──────────────────────────── M5 Dataset ────────────────────────────

@dataclass(frozen=True)
class M5Config:
    """M5 dataset file paths and constants."""
    sales_train_file: str = "sales_train_validation.csv"
    calendar_file: str = "calendar.csv"
    sell_prices_file: str = "sell_prices.csv"
    sales_train_eval_file: str = "sales_train_evaluation.csv"

    # M5 hierarchy structure
    num_items: int = 3049
    num_stores: int = 10
    num_bottom_series: int = 30490
    forecast_horizon: int = 28
    num_hierarchy_levels: int = 12

    # States and stores
    states: tuple = ("CA", "TX", "WI")
    stores_per_state: Dict[str, List[str]] = field(default_factory=lambda: {
        "CA": ["CA_1", "CA_2", "CA_3", "CA_4"],
        "TX": ["TX_1", "TX_2", "TX_3"],
        "WI": ["WI_1", "WI_2", "WI_3"],
    })

    # Categories and departments
    categories: tuple = ("FOODS", "HOBBIES", "HOUSEHOLD")
    departments: tuple = (
        "FOODS_1", "FOODS_2", "FOODS_3",
        "HOBBIES_1", "HOBBIES_2",
        "HOUSEHOLD_1", "HOUSEHOLD_2",
    )

    # Date columns in wide format
    day_col_prefix: str = "d_"
    first_day: int = 1
    last_train_day: int = 1913  # validation set
    last_eval_day: int = 1941   # evaluation set


# ──────────────────────────── Feature Engineering ────────────────────

@dataclass(frozen=True)
class FeatureConfig:
    """Feature engineering hyperparameters."""
    # Lag features
    lag_days: tuple = (7, 14, 21, 28)

    # Rolling window statistics
    rolling_windows: tuple = (7, 14, 28)
    rolling_aggregations: tuple = ("mean", "std", "min", "max")

    # Calendar features to extract
    calendar_features: tuple = (
        "wday", "month", "year", "week_of_year",
        "is_weekend", "quarter",
    )

    # Price features
    price_rolling_windows: tuple = (7, 14, 28)

    # Categorical encoding columns
    categorical_cols: tuple = (
        "item_id", "dept_id", "cat_id", "store_id", "state_id",
    )

    # Target column
    target_col: str = "sales"

    # Date column after melting
    date_col: str = "date"
    day_col: str = "d"

    # Minimum training samples required
    min_train_samples: int = 365

    # Processing chunk size (for memory management)
    chunk_size: int = 5000


# ──────────────────────────── Forecasting ────────────────────────────

@dataclass(frozen=True)
class LightGBMConfig:
    """LightGBM model hyperparameters."""
    objective: str = "tweedie"
    tweedie_variance_power: float = 1.1
    metric: str = "rmse"
    learning_rate: float = 0.05
    num_leaves: int = 127
    min_child_samples: int = 50
    max_depth: int = -1
    subsample: float = 0.7
    colsample_bytree: float = 0.7
    reg_alpha: float = 0.1
    reg_lambda: float = 0.1
    n_estimators: int = 1500
    early_stopping_rounds: int = 100
    verbose: int = -1
    n_jobs: int = -1
    seed: int = 42

    def to_dict(self) -> dict:
        """Convert to dict for LightGBM params."""
        return {
            "objective": self.objective,
            "tweedie_variance_power": self.tweedie_variance_power,
            "metric": self.metric,
            "learning_rate": self.learning_rate,
            "num_leaves": self.num_leaves,
            "min_child_samples": self.min_child_samples,
            "max_depth": self.max_depth,
            "subsample": self.subsample,
            "colsample_bytree": self.colsample_bytree,
            "reg_alpha": self.reg_alpha,
            "reg_lambda": self.reg_lambda,
            "verbose": self.verbose,
            "n_jobs": self.n_jobs,
            "seed": self.seed,
        }


@dataclass(frozen=True)
class TFTConfig:
    """Temporal Fusion Transformer hyperparameters."""
    max_encoder_length: int = 90
    max_prediction_length: int = 28
    batch_size: int = 128
    max_epochs: int = 50
    learning_rate: float = 0.001
    hidden_size: int = 64
    attention_head_size: int = 4
    dropout: float = 0.1
    hidden_continuous_size: int = 16
    gradient_clip_val: float = 0.5
    early_stop_patience: int = 5
    reduce_lr_patience: int = 3
    seed: int = 42

    # Device configuration
    accelerator: str = "auto"  # 'gpu' if available, else 'cpu'
    devices: int = 1

    # Data configuration
    time_varying_known_reals: tuple = (
        "time_idx", "month", "wday", "is_weekend",
        "snap_CA", "snap_TX", "snap_WI",
    )
    time_varying_unknown_reals: tuple = (
        "sales", "sell_price", "price_momentum",
    )
    static_categoricals: tuple = (
        "item_id", "store_id", "dept_id", "cat_id", "state_id",
    )


@dataclass(frozen=True)
class ReconciliationConfig:
    """Hierarchical reconciliation settings."""
    method: str = "bottom_up"  # 'bottom_up' or 'mint'
    # MinT settings
    mint_method: str = "shrink"  # 'ols', 'wls', 'shrink', 'mint_cov'


# ──────────────────────────── Causal ────────────────────────────

@dataclass(frozen=True)
class CausalConfig:
    """Causal inference configuration."""
    # Promotion detection
    price_drop_threshold: float = 0.10  # 10% price drop = promotion
    min_promotion_duration: int = 3  # minimum days
    max_promotion_duration: int = 28  # maximum days

    # DiD settings
    pre_period_days: int = 28
    post_period_days: int = 28
    min_control_items: int = 5

    # Synthetic control
    pre_treatment_periods: int = 60
    post_treatment_periods: int = 28

    # Refutation
    num_placebo_simulations: int = 100
    significance_level: float = 0.05


# ──────────────────────────── Pricing ────────────────────────────

@dataclass(frozen=True)
class PricingConfig:
    """Dynamic pricing (LinUCB) configuration."""
    # Price arms (multipliers relative to base price)
    price_multipliers: tuple = (0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20)
    num_arms: int = 9

    # LinUCB
    alpha: float = 1.5  # exploration parameter
    context_dim: int = 15  # dimension of context vector

    # Simulation
    num_rounds: int = 10000
    warmup_rounds: int = 500

    # Elasticity model
    default_elasticity: float = -1.5  # price elasticity of demand


# ──────────────────────────── Anomaly Detection ────────────────────

@dataclass(frozen=True)
class AnomalyConfig:
    """Anomaly detection configuration."""
    # STL
    stl_period: int = 7  # weekly seasonality
    stl_robust: bool = True
    residual_zscore_threshold: float = 3.0

    # Isolation Forest
    contamination: float = 0.05
    n_estimators: int = 200
    max_samples: str = "auto"
    random_state: int = 42

    # SHAP
    shap_max_samples: int = 1000

    # Anomaly types
    anomaly_categories: tuple = (
        "demand_spike", "stockout", "data_error", "seasonal_shift",
    )


# ──────────────────────────── API ────────────────────────────

@dataclass(frozen=True)
class APIConfig:
    """FastAPI and dashboard configuration."""
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    dashboard_port: int = 8501

    # Redis caching (optional)
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_ttl: int = 3600  # cache TTL in seconds
    use_redis: bool = os.getenv("USE_REDIS", "false").lower() == "true"

    # CORS
    allowed_origins: tuple = ("*",)


# ──────────────────────────── MLflow ────────────────────────────

@dataclass(frozen=True)
class MLflowConfig:
    """MLflow tracking configuration."""
    tracking_uri: str = f"file:///{MLFLOW_DIR.as_posix()}"
    experiment_name: str = "demand_intelligence_platform"
    registry_uri: str = f"file:///{MLFLOW_DIR.as_posix()}"


# ──────────────────────────── Instantiate Configs ────────────────────

m5 = M5Config()
features = FeatureConfig()
lgbm = LightGBMConfig()
tft = TFTConfig()
reconciliation = ReconciliationConfig()
causal = CausalConfig()
pricing = PricingConfig()
anomaly = AnomalyConfig()
api = APIConfig()
mlflow_cfg = MLflowConfig()
