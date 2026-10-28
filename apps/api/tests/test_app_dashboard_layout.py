"""Tests for App Dashboard Layout — save, load, default."""

import pytest

from app.services.app_dashboard_layout import AppDashboardLayout

WIDGETS = [
    {"widget_id": "w1", "type": "chart", "title": "Revenue", "col": 0, "row": 0, "width": 2, "height": 1},
    {"widget_id": "w2", "type": "metric", "title": "Users", "col": 2, "row": 0},
]


class TestSave:
    def test_save(self):
        d = AppDashboardLayout()
        l = d.save_layout("inst-1", "main", "Main Dashboard", WIDGETS, is_default=True)
        assert len(l.widgets) == 2
        assert l.is_default is True

    def test_widget_positions(self):
        d = AppDashboardLayout()
        l = d.save_layout("inst-1", "main", "Main", WIDGETS)
        assert l.widgets[0].width == 2


class TestLoad:
    def test_get(self):
        d = AppDashboardLayout()
        d.save_layout("inst-1", "main", "Main", WIDGETS)
        l = d.get_layout("inst-1", "main")
        assert l.name == "Main"

    def test_not_found(self):
        d = AppDashboardLayout()
        with pytest.raises(KeyError):
            d.get_layout("inst-1", "nope")

    def test_default(self):
        d = AppDashboardLayout()
        d.save_layout("inst-1", "main", "Main", WIDGETS, is_default=True)
        d.save_layout("inst-1", "alt", "Alt", WIDGETS)
        default = d.get_default("inst-1")
        assert default is not None
        assert default.layout_id == "main"


class TestList:
    def test_list(self):
        d = AppDashboardLayout()
        d.save_layout("inst-1", "a", "A", WIDGETS)
        d.save_layout("inst-1", "b", "B", WIDGETS)
        assert len(d.list_layouts("inst-1")) == 2


class TestIsolation:
    def test_cross(self):
        d = AppDashboardLayout()
        d.save_layout("inst-1", "main", "Main", WIDGETS)
        assert d.list_layouts("inst-2") == []
