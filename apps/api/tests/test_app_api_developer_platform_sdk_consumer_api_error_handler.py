"""Tests for Consumer API Error Handler service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_error_handler import (
    ErrorHandler, ErrorPolicy, ErrorOccurrence,
)


class TestErrorHandler:
    def test_handle_with_policy(self):
        svc = ErrorHandler()
        svc.set_policy(ErrorPolicy("RATE_LIMIT", retryable=True, max_retries=5, backoff_ms=2000))
        result = svc.handle(ErrorOccurrence("RATE_LIMIT", "ep1", "Too many requests"))
        assert result["retryable"] is True
        assert result["max_retries"] == 5

    def test_handle_without_policy(self):
        svc = ErrorHandler()
        result = svc.handle(ErrorOccurrence("UNKNOWN", "ep1", "Something went wrong"))
        assert result["retryable"] is False
        assert result["policy"] == "default"

    def test_fallback_response(self):
        svc = ErrorHandler()
        svc.set_policy(ErrorPolicy("SERVICE_DOWN", fallback_response={"data": [], "cached": True}))
        result = svc.handle(ErrorOccurrence("SERVICE_DOWN", "ep1", "Service unavailable"))
        assert result["fallback"] == {"data": [], "cached": True}

    def test_alert_threshold(self):
        svc = ErrorHandler()
        svc.set_policy(ErrorPolicy("TIMEOUT", alert_on_count=3))
        svc.handle(ErrorOccurrence("TIMEOUT", "ep1", "Timeout"))
        svc.handle(ErrorOccurrence("TIMEOUT", "ep1", "Timeout"))
        result = svc.handle(ErrorOccurrence("TIMEOUT", "ep1", "Timeout"))
        assert result.get("alert_triggered") is True

    def test_occurrence_count(self):
        svc = ErrorHandler()
        svc.handle(ErrorOccurrence("ERR_1", "ep1", "Error"))
        svc.handle(ErrorOccurrence("ERR_1", "ep1", "Error"))
        result = svc.handle(ErrorOccurrence("ERR_1", "ep1", "Error"))
        assert result["occurrence_count"] == 3

    def test_error_summary(self):
        svc = ErrorHandler()
        for _ in range(5):
            svc.handle(ErrorOccurrence("ERR_A", "ep1", "A"))
        for _ in range(3):
            svc.handle(ErrorOccurrence("ERR_B", "ep2", "B"))
        summary = svc.get_error_summary()
        assert summary["total_errors"] == 8
        assert summary["unique_codes"] == 2
        assert summary["top_errors"][0]["code"] == "ERR_A"

    def test_get_alerts(self):
        svc = ErrorHandler()
        svc.set_policy(ErrorPolicy("X", alert_on_count=1))
        svc.handle(ErrorOccurrence("X", "ep1", "err"))
        alerts = svc.get_alerts()
        assert len(alerts) == 1

    def test_list_policies(self):
        svc = ErrorHandler()
        svc.set_policy(ErrorPolicy("A", retryable=True))
        svc.set_policy(ErrorPolicy("B", retryable=False))
        assert len(svc.list_policies()) == 2

    def test_clear_counts(self):
        svc = ErrorHandler()
        svc.handle(ErrorOccurrence("X", "ep1", "err"))
        svc.clear_counts()
        result = svc.handle(ErrorOccurrence("X", "ep1", "err"))
        assert result["occurrence_count"] == 1

    def test_invalid_max_retries(self):
        svc = ErrorHandler()
        with pytest.raises(ValueError):
            svc.set_policy(ErrorPolicy("X", max_retries=-1))

    def test_isolation(self):
        a, b = ErrorHandler(), ErrorHandler()
        a.handle(ErrorOccurrence("X", "ep1", "err"))
        assert b.get_error_summary()["total_errors"] == 0
