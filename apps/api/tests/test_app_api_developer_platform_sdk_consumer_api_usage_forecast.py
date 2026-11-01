"""Tests for API Usage Forecast service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_usage_forecast import UsageForecast


class TestUsageForecast:
    def test_add_and_summary(self):
        svc = UsageForecast()
        for i in range(5):
            svc.add_data("requests", f"2024-{i+1:02d}", 100.0 + i * 10)
        summary = svc.get_summary("requests")
        assert summary["data_points"] == 5
        assert summary["min"] == 100.0
        assert summary["max"] == 140.0

    def test_trend_increasing(self):
        svc = UsageForecast()
        for i in range(10):
            svc.add_data("m1", f"p{i}", 100.0 + i * 20)
        trend = svc.get_trend("m1")
        assert trend["direction"] == "increasing"
        assert trend["growth_rate"] > 0

    def test_trend_decreasing(self):
        svc = UsageForecast()
        for i in range(10):
            svc.add_data("m1", f"p{i}", 200.0 - i * 15)
        trend = svc.get_trend("m1")
        assert trend["direction"] == "decreasing"

    def test_trend_stable(self):
        svc = UsageForecast()
        for i in range(10):
            svc.add_data("m1", f"p{i}", 100.0)
        trend = svc.get_trend("m1")
        assert trend["direction"] == "stable"

    def test_forecast(self):
        svc = UsageForecast()
        for i in range(6):
            svc.add_data("m1", f"p{i}", 100.0 + i * 10)
        result = svc.forecast("m1", 3)
        assert len(result["forecasted_values"]) == 3
        assert result["forecasted_values"][0] > 0

    def test_forecast_insufficient(self):
        svc = UsageForecast()
        svc.add_data("m1", "p0", 100)
        result = svc.forecast("m1")
        assert result["error"] == "insufficient_data"

    def test_anomaly_detection(self):
        svc = UsageForecast()
        for i in range(10):
            svc.add_data("m1", f"p{i}", 100.0)
        svc.add_data("m1", "p10", 500.0)  # spike
        anomalies = svc.detect_anomalies("m1")
        assert len(anomalies) >= 1
        assert anomalies[0]["type"] == "spike"

    def test_negative_value_rejected(self):
        svc = UsageForecast()
        with pytest.raises(ValueError):
            svc.add_data("m1", "p0", -10)

    def test_list_metrics(self):
        svc = UsageForecast()
        svc.add_data("b", "p0", 1)
        svc.add_data("a", "p0", 2)
        assert svc.list_metrics() == ["a", "b"]

    def test_isolation(self):
        a, b = UsageForecast(), UsageForecast()
        a.add_data("m1", "p0", 100)
        assert b.get_summary("m1")["status"] == "no_data"
