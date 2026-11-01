"""HealthScore to_dict detailed tests."""

import pytest
from app.services.app_health_monitor import HealthScore

CASES = [
    (0, 0, 0),
    (100, 0, 0),
    (100, 50, 0),
    (100, 0, 50),
    (100, 25, 25),
    (1000, 100, 50),
]

@pytest.mark.parametrize("total,failed,timeout", CASES)
def test_to_dict_has_all_keys(total, failed, timeout):
    h = HealthScore(total, failed, timeout)
    d = h.to_dict()
    assert set(d.keys()) == {"score", "status", "error_rate_pct", "total_executions", "failed_executions", "timeout_executions"}

@pytest.mark.parametrize("total,failed,timeout", CASES)
def test_to_dict_values_match(total, failed, timeout):
    h = HealthScore(total, failed, timeout)
    d = h.to_dict()
    assert d["total_executions"] == total
    assert d["failed_executions"] == failed
    assert d["timeout_executions"] == timeout
    assert d["score"] == h.score
    assert d["status"] == h.status
