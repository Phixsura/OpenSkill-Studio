"""Tests for health score computation."""

from app.services.app_health_monitor import HealthScore, compute_health_score


def test_perfect_health():
    h = HealthScore(100, 0, 0)
    assert h.score == 100
    assert h.status == "healthy"

def test_no_data():
    h = HealthScore(0, 0, 0)
    assert h.score == 100
    assert h.status == "healthy"

def test_degraded():
    h = HealthScore(100, 10, 5)
    assert h.score == 85
    assert h.status == "degraded"

def test_warning():
    h = HealthScore(100, 30, 5)
    assert h.score == 65
    assert h.status == "warning"

def test_critical():
    h = HealthScore(100, 40, 20)
    assert h.score == 40
    assert h.status == "critical"

def test_all_failed():
    h = HealthScore(10, 10, 0)
    assert h.score == 0
    assert h.status == "critical"

def test_error_rate():
    h = HealthScore(100, 5, 5)
    assert h.error_rate == 10.0

def test_error_rate_zero():
    h = HealthScore(0, 0, 0)
    assert h.error_rate == 0.0

def test_to_dict():
    h = HealthScore(50, 5, 2)
    d = h.to_dict()
    assert d["score"] == 86
    assert d["status"] == "degraded"
    assert d["total_executions"] == 50
    assert d["failed_executions"] == 5
    assert d["timeout_executions"] == 2
    assert d["error_rate_pct"] == 14.0

def test_compute_health_score_importable():
    import asyncio
    assert asyncio.iscoroutinefunction(compute_health_score)
