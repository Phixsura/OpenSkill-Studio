"""Parametrized health score computation tests."""

import pytest
from app.services.app_health_monitor import HealthScore

SCORES = [
    (100, 0, 0, 100, "healthy"),
    (100, 5, 0, 95, "healthy"),
    (100, 6, 0, 94, "degraded"),
    (100, 20, 0, 80, "degraded"),
    (100, 21, 0, 79, "warning"),
    (100, 50, 0, 50, "warning"),
    (100, 51, 0, 49, "critical"),
    (100, 100, 0, 0, "critical"),
    (0, 0, 0, 100, "healthy"),
    (50, 0, 5, 90, "degraded"),
    (200, 10, 10, 90, "degraded"),
    (1000, 5, 5, 99, "healthy"),
]

@pytest.mark.parametrize("total,failed,timeout,expected_score,expected_status", SCORES)
def test_health_score(total, failed, timeout, expected_score, expected_status):
    h = HealthScore(total, failed, timeout)
    assert h.score == expected_score, f"Score: {h.score} != {expected_score}"
    assert h.status == expected_status, f"Status: {h.status} != {expected_status}"
