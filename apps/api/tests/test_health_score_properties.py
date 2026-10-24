"""HealthScore mathematical properties."""

import pytest
from app.services.app_health_monitor import HealthScore

def test_score_never_negative():
    for failed in range(0, 201, 10):
        h = HealthScore(100, failed, 0)
        assert h.score >= 0

def test_score_never_exceeds_100():
    for total in range(0, 1001, 100):
        h = HealthScore(total, 0, 0)
        assert h.score <= 100

def test_monotonic_decrease():
    """More failures → lower or equal score."""
    prev = 100
    for failed in range(0, 101):
        h = HealthScore(100, failed, 0)
        assert h.score <= prev
        prev = h.score

def test_timeout_counts_as_failure():
    h_fail = HealthScore(100, 10, 0)
    h_timeout = HealthScore(100, 0, 10)
    assert h_fail.score == h_timeout.score

def test_mixed_failures():
    h = HealthScore(100, 5, 5)
    assert h.score == 90

STATUS_BOUNDARIES = [
    (95, "healthy"),
    (94, "degraded"),
    (80, "degraded"),
    (79, "warning"),
    (50, "warning"),
    (49, "critical"),
    (0, "critical"),
    (100, "healthy"),
]

@pytest.mark.parametrize("score_val,expected_status", STATUS_BOUNDARIES)
def test_status_boundaries(score_val, expected_status):
    # Reverse-engineer total/failed to get desired score
    total = 100
    failed = total - score_val
    h = HealthScore(total, failed, 0)
    assert h.status == expected_status
