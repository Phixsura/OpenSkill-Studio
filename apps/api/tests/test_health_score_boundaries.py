"""Boundary tests for health score thresholds."""

import pytest
from app.services.app_health_monitor import HealthScore


@pytest.mark.parametrize("total,failed,timeout,expected_status", [
    (100, 0, 0, "healthy"),      # 100% → healthy
    (100, 3, 2, "healthy"),      # 95% → healthy
    (100, 5, 0, "healthy"),      # exactly 95% → healthy
    (100, 5, 1, "degraded"),     # 94% → degraded
    (100, 15, 5, "degraded"),    # 80% → degraded
    (100, 20, 1, "warning"),     # 79% → warning
    (100, 40, 10, "warning"),    # 50% → warning boundary
    (100, 50, 1, "critical"),    # 49% → critical
    (100, 100, 0, "critical"),   # 0% → critical
    (0, 0, 0, "healthy"),        # no data → healthy
    (1, 0, 0, "healthy"),        # single success → healthy
    (1, 1, 0, "critical"),       # single failure → critical
    (1000, 10, 5, "healthy"),    # 1.5% → healthy
])
def test_health_score_boundaries(total, failed, timeout, expected_status):
    h = HealthScore(total, failed, timeout)
    assert h.status == expected_status, f"Expected {expected_status} for {total}/{failed}/{timeout}, got {h.status} (score={h.score})"
