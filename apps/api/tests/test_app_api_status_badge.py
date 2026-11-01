"""Tests for App API Status Badge — create, update, views."""

import pytest
from app.services.app_api_status_badge import AppAPIStatusBadge


class TestCreate:
    def test_create(self):
        b = AppAPIStatusBadge()
        badge = b.create("inst-1", "b1", "build", "passing", "green")
        assert badge.label == "build"

    def test_invalid_color(self):
        b = AppAPIStatusBadge()
        with pytest.raises(ValueError):
            b.create("inst-1", "b1", "build", "ok", "purple")


class TestUpdate:
    def test_update_status(self):
        b = AppAPIStatusBadge()
        b.create("inst-1", "b1", "build", "passing")
        badge = b.update_status("inst-1", "b1", "failing", "red")
        assert badge.status == "failing"
        assert badge.color == "red"

    def test_views(self):
        b = AppAPIStatusBadge()
        b.create("inst-1", "b1", "build", "passing")
        b.record_view("inst-1", "b1")
        b.record_view("inst-1", "b1")
        assert b.list_badges("inst-1")[0].views == 2


class TestIsolation:
    def test_cross(self):
        b = AppAPIStatusBadge()
        b.create("inst-1", "b1", "build", "ok")
        assert b.list_badges("inst-2") == []
