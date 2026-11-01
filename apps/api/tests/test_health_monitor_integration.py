"""HealthScore integration with app_lifecycle."""

from app.services.app_health_monitor import HealthScore
from app.services.app_lifecycle import check_app_health
import asyncio

def test_health_score_consistent_with_lifecycle():
    """HealthScore thresholds match lifecycle health status logic."""
    # healthy ≥ 95
    assert HealthScore(100, 5, 0).status == "healthy"
    assert HealthScore(100, 4, 0).status == "healthy"
    # degraded 80-94
    assert HealthScore(100, 6, 0).status == "degraded"
    assert HealthScore(100, 20, 0).status == "degraded"
    # warning 50-79
    assert HealthScore(100, 21, 0).status == "warning"
    assert HealthScore(100, 50, 0).status == "warning"
    # critical < 50
    assert HealthScore(100, 51, 0).status == "critical"
    assert HealthScore(100, 100, 0).status == "critical"

def test_check_app_health_is_async():
    assert asyncio.iscoroutinefunction(check_app_health)

def test_score_to_dict_format():
    h = HealthScore(100, 10, 5)
    d = h.to_dict()
    assert set(d.keys()) == {"score", "status", "error_rate_pct", "total_executions", "failed_executions", "timeout_executions"}
