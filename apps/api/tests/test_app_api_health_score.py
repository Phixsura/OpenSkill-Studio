"""Tests for App API Health Score — dimensions, composite."""

import pytest
from app.services.app_api_health_score import AppAPIHealthScore


class TestDimension:
    def test_add(self):
        h = AppAPIHealthScore()
        d = h.add_dimension("inst-1", "uptime", "Uptime", weight=3.0)
        assert d.score == 100.0


class TestScore:
    def test_composite(self):
        h = AppAPIHealthScore()
        h.add_dimension("inst-1", "uptime", "Uptime", weight=3.0)
        h.add_dimension("inst-1", "latency", "Latency", weight=1.0)
        h.update_score("inst-1", "uptime", 90.0)
        h.update_score("inst-1", "latency", 70.0)
        # (90*3 + 70*1) / 4 = 85.0
        assert h.composite_score("inst-1") == 85.0

    def test_invalid_score(self):
        h = AppAPIHealthScore()
        h.add_dimension("inst-1", "d1", "D")
        with pytest.raises(ValueError):
            h.update_score("inst-1", "d1", 150)

    def test_empty(self):
        h = AppAPIHealthScore()
        assert h.composite_score("inst-1") == 100.0


class TestIsolation:
    def test_cross(self):
        h = AppAPIHealthScore()
        h.add_dimension("inst-1", "d1", "D")
        assert h.list_dimensions("inst-2") == []
