"""Tests for App User Preference — get/set, defaults, bulk, reset."""

import pytest

from app.services.app_user_preference import AppUserPreference, PreferenceSchema


@pytest.fixture
def prefs():
    p = AppUserPreference()
    p.define_schema("inst-1", [
        PreferenceSchema(key="theme", default_value="light", description="UI theme"),
        PreferenceSchema(key="language", default_value="en"),
        PreferenceSchema(key="notifications", default_value=True),
    ])
    return p


class TestSetGet:
    def test_set_and_get(self, prefs):
        prefs.set_preference("inst-1", "user-1", "theme", "dark")
        assert prefs.get_preference("inst-1", "user-1", "theme") == "dark"

    def test_default_value(self, prefs):
        assert prefs.get_preference("inst-1", "user-1", "theme") == "light"

    def test_unknown_key_rejected(self, prefs):
        with pytest.raises(ValueError, match="Unknown"):
            prefs.set_preference("inst-1", "user-1", "unknown_key", "val")

    def test_no_schema_allows_any(self):
        p = AppUserPreference()
        p.set_preference("inst-1", "user-1", "anything", "val")
        assert p.get_preference("inst-1", "user-1", "anything") == "val"

    def test_missing_returns_none(self):
        p = AppUserPreference()
        assert p.get_preference("inst-1", "user-1", "nope") is None


class TestGetAll:
    def test_defaults_filled(self, prefs):
        all_prefs = prefs.get_all("inst-1", "user-1")
        assert all_prefs["theme"] == "light"
        assert all_prefs["language"] == "en"

    def test_overrides(self, prefs):
        prefs.set_preference("inst-1", "user-1", "theme", "dark")
        all_prefs = prefs.get_all("inst-1", "user-1")
        assert all_prefs["theme"] == "dark"
        assert all_prefs["language"] == "en"


class TestBulk:
    def test_set_bulk(self, prefs):
        count = prefs.set_bulk("inst-1", "user-1", {"theme": "dark", "language": "ja"})
        assert count == 2
        assert prefs.get_preference("inst-1", "user-1", "language") == "ja"


class TestReset:
    def test_reset_single(self, prefs):
        prefs.set_preference("inst-1", "user-1", "theme", "dark")
        prefs.reset_preference("inst-1", "user-1", "theme")
        assert prefs.get_preference("inst-1", "user-1", "theme") == "light"

    def test_reset_all(self, prefs):
        prefs.set_bulk("inst-1", "user-1", {"theme": "dark", "language": "ja"})
        count = prefs.reset_all("inst-1", "user-1")
        assert count == 2
        assert prefs.get_preference("inst-1", "user-1", "theme") == "light"


class TestIsolation:
    def test_cross_user(self, prefs):
        prefs.set_preference("inst-1", "user-1", "theme", "dark")
        assert prefs.get_preference("inst-1", "user-2", "theme") == "light"

    def test_cross_installation(self, prefs):
        prefs.set_preference("inst-1", "user-1", "theme", "dark")
        assert prefs.get_preference("inst-2", "user-1", "theme") is None
