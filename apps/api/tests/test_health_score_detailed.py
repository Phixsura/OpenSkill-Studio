"""Detailed HealthScore tests — boundary conditions and edge cases."""

import pytest
from app.services.app_health_monitor import HealthScore

SCORE_CASES = [
    (0, 0, 0, 100, "healthy"),     # no data
    (100, 0, 0, 100, "healthy"),   # perfect
    (100, 5, 0, 95, "healthy"),    # boundary
    (100, 6, 0, 94, "degraded"),   # just degraded
    (100, 20, 0, 80, "degraded"),  # boundary
    (100, 21, 0, 79, "warning"),   # just warning
    (100, 50, 0, 50, "warning"),   # boundary
    (100, 51, 0, 49, "critical"),  # just critical
    (100, 100, 0, 0, "critical"),  # all failed
    (100, 0, 100, 0, "critical"),  # all timeout
    (100, 50, 50, 0, "critical"),  # mixed fail+timeout
    (1, 1, 0, 0, "critical"),     # single failure
    (1, 0, 0, 100, "healthy"),    # single success
    (1000, 10, 5, 98, "healthy"), # large scale low error
]

@pytest.mark.parametrize("total,failed,timeout,expected_score,expected_status", SCORE_CASES,
    ids=lambda x: str(x))
def test_score(total, failed, timeout, expected_score, expected_status):
    h = HealthScore(total, failed, timeout)
    assert h.score == expected_score
    assert h.status == expected_status

def test_error_rate_zero():
    h = HealthScore(0, 0, 0)
    assert h.error_rate == 0.0

def test_error_rate_half():
    h = HealthScore(100, 50, 0)
    assert abs(h.error_rate - 50.0) < 0.1

def test_to_dict_keys():
    h = HealthScore(100, 10, 5)
    d = h.to_dict()
    assert set(d.keys()) == {"score", "status", "error_rate_pct", "total_executions", "failed_executions", "timeout_executions"}

def test_to_dict_values():
    h = HealthScore(200, 20, 10)
    d = h.to_dict()
    assert d["total_executions"] == 200
    assert d["failed_executions"] == 20
    assert d["timeout_executions"] == 10
