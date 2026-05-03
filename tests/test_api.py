"""
FastAPI endpoint integration tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data

    def test_health_has_timing_header(self):
        response = client.get("/health")
        assert "x-process-time" in response.headers


class TestForecastEndpoint:
    def test_forecast_valid_request(self):
        payload = {"item_id": "FOODS_3_090", "store_id": "CA_1", "horizon": 28}
        response = client.post("/forecast", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == "FOODS_3_090"
        assert len(data["forecasts"]) == 28

    def test_forecast_custom_horizon(self):
        payload = {"item_id": "FOODS_3_090", "store_id": "CA_1", "horizon": 7}
        response = client.post("/forecast", json=payload)
        data = response.json()
        assert len(data["forecasts"]) == 7

    def test_forecast_invalid_horizon(self):
        payload = {"item_id": "FOODS_3_090", "store_id": "CA_1", "horizon": 100}
        response = client.post("/forecast", json=payload)
        assert response.status_code == 422  # Validation error


class TestPricingEndpoint:
    def test_pricing_valid_request(self):
        payload = {
            "item_id": "FOODS_3_090", "store_id": "CA_1",
            "current_price": 3.99, "forecast_demand": 25.0,
        }
        response = client.post("/pricing/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["recommended_price"] > 0
        assert "price_multiplier" in data


class TestAnomalyEndpoint:
    def test_anomaly_returns_data(self):
        response = client.get("/anomalies/FOODS_3_090?lookback_days=30")
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == "FOODS_3_090"
        assert "anomalies_detected" in data


class TestModelRegistry:
    def test_model_registry(self):
        response = client.get("/model-registry")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "total" in data
