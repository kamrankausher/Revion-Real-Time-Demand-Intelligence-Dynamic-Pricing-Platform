# 🧠 ⚡ Revion

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)
![LightGBM](https://img.shields.io/badge/LightGBM-4.3-green?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2-EE4C2C?style=for-the-badge&logo=pytorch)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![MLflow](https://img.shields.io/badge/MLflow-2.11-0194E2?style=for-the-badge&logo=mlflow)

**Production-grade ML system for demand forecasting, causal promotion analysis, dynamic pricing, and anomaly detection on the Walmart M5 dataset (42,840 time series).**

</div>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           ⚡ Revion                              │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Data     │Forecasting│ Causal   │ Dynamic  │ Anomaly  │ API &    │
│ Pipeline │ Engine   │ Engine   │ Pricing  │ Detection│Dashboard │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│Ingestion │LightGBM  │DiD/DoWhy │LinUCB    │STL Decomp│FastAPI   │
│Features  │TFT       │Synthetic │Elasticity│IsoForest │Streamlit │
│Parquet   │Hierarchy │Control   │Simulator │SHAP      │MLflow    │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

## 📁 Project Structure

```
├── src/
│   ├── config.py                    # Central configuration (dataclasses)
│   ├── data_pipeline/
│   │   ├── ingestion.py             # M5 data loading & merging
│   │   ├── feature_engineering.py   # Lag/rolling/calendar/price features
│   │   ├── feature_store.py         # Partitioned Parquet persistence
│   │   └── eda.py                   # Automated EDA diagnostics
│   ├── forecasting/
│   │   ├── lightgbm_model.py        # LightGBM Tweedie regressor
│   │   ├── tft_model.py             # Temporal Fusion Transformer
│   │   ├── reconciliation.py        # Hierarchical reconciliation (12-level)
│   │   ├── metrics.py               # WRMSSE + standard metrics
│   │   └── train.py                 # Training orchestrator + MLflow
│   ├── causal/
│   │   ├── did_analysis.py          # Difference-in-Differences + DoWhy
│   │   ├── synthetic_control.py     # Synthetic control method
│   │   ├── promotion_effects.py     # Promotion lift aggregation
│   │   └── visualization.py         # Causal analysis plots
│   ├── pricing/
│   │   ├── linucb_bandit.py         # LinUCB contextual bandit
│   │   ├── demand_model.py          # Price elasticity estimation
│   │   ├── simulator.py             # Pricing simulation environment
│   │   └── optimizer.py             # End-to-end pricing pipeline
│   ├── anomaly/
│   │   ├── stl_detector.py          # STL decomposition detector
│   │   ├── isolation_forest.py      # Isolation Forest detector
│   │   └── explainer.py             # SHAP-based explanations
│   ├── api/
│   │   └── app.py                   # FastAPI REST endpoints
│   └── dashboard/
│       └── streamlit_app.py         # Premium Streamlit dashboard
├── tests/
│   ├── test_bandit.py               # LinUCB unit tests
│   ├── test_anomaly.py              # Anomaly detection tests
│   ├── test_metrics.py              # Forecasting metrics tests
│   └── test_api.py                  # FastAPI integration tests
├── docker/
│   ├── Dockerfile                   # Multi-stage production image
│   └── docker-compose.yml           # API + Dashboard + MLflow
├── .github/workflows/ci.yml         # CI/CD pipeline
├── requirements.txt                 # Pinned dependencies
└── setup.py                         # Package installation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Walmart M5 Dataset](https://www.kaggle.com/c/m5-forecasting-accuracy) (place in `data/raw/`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/demand-intelligence-platform.git
cd demand-intelligence-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### Start the API

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Start the Dashboard

```bash
streamlit run src/dashboard/streamlit_app.py
```

### Docker Deployment

```bash
cd docker
docker-compose up --build
```
This starts:
- **API**: `http://localhost:8000` (FastAPI + Swagger UI at `/docs`)
- **Dashboard**: `http://localhost:8501` (Streamlit)
- **MLflow**: `http://localhost:5000` (Experiment tracking)

---

## 📊 Component Details

### 1. Data Pipeline
| Component | Description |
|-----------|-------------|
| **Ingestion** | Loads M5 CSVs, melts wide→long, merges calendar + prices |
| **Feature Engineering** | Stateful pipeline: lags, rolling stats, calendar extraction, label encoding |
| **Feature Store** | Partitioned Parquet for efficient I/O |
| **EDA** | Automated distribution, seasonality, and missing data analysis |

### 2. Forecasting Engine
| Model | Approach | Key Feature |
|-------|----------|-------------|
| **LightGBM** | Tweedie objective, recursive multi-step | WRMSSE-optimized |
| **TFT** | Attention-based deep learning | Interpretability (attention weights) |
| **Reconciliation** | Bottom-up + MinT | 12-level M5 hierarchy coherence |

### 3. Causal Promotion Engine
| Method | Use Case |
|--------|----------|
| **Difference-in-Differences** | Item-level promotion lift with DoWhy |
| **Synthetic Control** | Store-level treatment effects |
| **Parallel Trends Test** | DiD assumption validation |
| **Placebo Refutation** | Robustness verification |

### 4. Dynamic Pricing (LinUCB Bandit)
- **9 price arms**: 0.80x – 1.20x multipliers
- **15-dimensional context**: forecast, price, calendar, category features
- **Log-linear elasticity model** for demand response
- **Convergence diagnostics** with regret analysis

### 5. Anomaly Detection
| Detector | Method |
|----------|--------|
| **STL** | Seasonal-trend decomposition → residual z-scores |
| **Isolation Forest** | Multi-feature unsupervised detection |
| **SHAP Explainer** | Human-readable anomaly explanations |

### 6. API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check + uptime |
| `/forecast` | POST | Generate demand forecast |
| `/pricing/recommend` | POST | Dynamic pricing recommendation |
| `/anomalies/{item_id}` | GET | Anomaly detection results |
| `/promotion-impact/{item}/{store}` | GET | Causal promotion impact |
| `/model-registry` | GET | List loaded models |

---

## 🧪 Testing

```
30 tests across 4 test files:
├── test_bandit.py    (9 tests)  — LinUCB arm UCB, agent selection, regret
├── test_anomaly.py   (7 tests)  — STL decomposition, IsoForest, SHAP
├── test_metrics.py   (6 tests)  — RMSE, MAE, MAPE, SMAPE, perfect prediction
└── test_api.py       (8 tests)  — All REST endpoints, validation, timing
```

## 🔧 Configuration

All hyperparameters are centralized in `src/config.py` using frozen dataclasses:

```python
from src.config import lgbm, tft, pricing, anomaly

lgbm.learning_rate    # 0.05
tft.hidden_size       # 64
pricing.alpha         # 1.5 (exploration parameter)
anomaly.contamination # 0.05
```

## 📦 Tech Stack

| Category | Technologies |
|----------|-------------|
| **ML/DL** | LightGBM, PyTorch, pytorch-forecasting, scikit-learn |
| **Causal** | DoWhy, statsmodels, scipy |
| **API** | FastAPI, Pydantic, uvicorn |
| **Dashboard** | Streamlit, Plotly |
| **MLOps** | MLflow, Docker, GitHub Actions |
| **Data** | pandas, PyArrow, NumPy |

---

## 📜 License

MIT License

## 👤 Author

Built as a production-grade ML systems engineering portfolio project.
