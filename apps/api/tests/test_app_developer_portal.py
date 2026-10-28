"""Tests for App Developer Portal — configure, sections, theme."""

import pytest

from app.services.app_developer_portal import AppDeveloperPortal


class TestConfigure:
    def test_configure(self):
        p = AppDeveloperPortal()
        config = p.configure("inst-1", "My Dev Portal", theme_color="#3B82F6")
        assert config.portal_name == "My Dev Portal"
        assert config.theme_color == "#3B82F6"


class TestSections:
    def test_add_section(self):
        p = AppDeveloperPortal()
        p.configure("inst-1", "Portal")
        s = p.add_section("inst-1", "s1", "Getting Started", [
            {"label": "Quickstart", "href": "/docs/quickstart"},
            {"label": "Auth", "href": "/docs/auth"},
        ])
        assert len(s.items) == 2

    def test_sorted(self):
        p = AppDeveloperPortal()
        p.configure("inst-1", "Portal")
        p.add_section("inst-1", "s2", "API Reference", [], sort_order=2)
        p.add_section("inst-1", "s1", "Getting Started", [], sort_order=1)
        config = p.get_portal("inst-1")
        assert config.sections[0].title == "Getting Started"


class TestTheme:
    def test_update(self):
        p = AppDeveloperPortal()
        p.configure("inst-1", "Portal")
        config = p.update_theme("inst-1", "#FF0000")
        assert config.theme_color == "#FF0000"


class TestIsolation:
    def test_cross(self):
        p = AppDeveloperPortal()
        p.configure("inst-1", "Portal")
        with pytest.raises(KeyError):
            p.get_portal("inst-2")
