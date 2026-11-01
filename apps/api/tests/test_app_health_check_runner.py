"""Health check runner tests."""
import pytest
import asyncio
from app.services.app_health_check_runner import run_health_check, format_health_result, aggregate_health

def test_run_returns_dict():
    result = asyncio.run(run_health_check(app_id="a1"))
    assert result["app_id"] == "a1"
    assert result["status"] == "healthy"

def test_format_healthy():
    assert "✅" in format_health_result({"status": "healthy", "latency_ms": 50})

def test_format_unhealthy():
    assert "❌" in format_health_result({"status": "critical", "latency_ms": 5000})

def test_aggregate_all_healthy():
    r = aggregate_health([{"status": "healthy"}, {"status": "healthy"}])
    assert r["overall"] == "healthy"
    assert r["healthy"] == 2

def test_aggregate_mixed():
    r = aggregate_health([{"status": "healthy"}, {"status": "degraded"}])
    assert r["overall"] == "degraded"
    assert r["unhealthy"] == 1

def test_aggregate_empty():
    r = aggregate_health([])
    assert r["overall"] == "unknown"
