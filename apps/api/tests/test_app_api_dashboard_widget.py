"""Tests for App API Dashboard Widget — register, refresh, filter."""

import pytest
from app.services.app_api_dashboard_widget import AppAPIDashboardWidget


class TestRegister:
    def test_register(self):
        d = AppAPIDashboardWidget()
        w = d.register("inst-1", "w1", "chart", "Revenue", "/api/revenue")
        assert w.widget_type == "chart"

    def test_invalid_type(self):
        d = AppAPIDashboardWidget()
        with pytest.raises(ValueError):
            d.register("inst-1", "w1", "sparkline", "X", "/api")


class TestRefresh:
    def test_count(self):
        d = AppAPIDashboardWidget()
        d.register("inst-1", "w1", "metric", "Users", "/api/users")
        d.record_refresh("inst-1", "w1")
        assert d.list_widgets("inst-1")[0].refresh_count == 1


class TestFilter:
    def test_by_type(self):
        d = AppAPIDashboardWidget()
        d.register("inst-1", "w1", "chart", "A", "/a")
        d.register("inst-1", "w2", "metric", "B", "/b")
        assert len(d.by_type("inst-1", "chart")) == 1


class TestIsolation:
    def test_cross(self):
        d = AppAPIDashboardWidget()
        d.register("inst-1", "w1", "chart", "A", "/a")
        assert d.list_widgets("inst-2") == []
