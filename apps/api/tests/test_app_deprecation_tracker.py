"""Tests for App Deprecation Tracker — deprecate, usage, migration."""

import pytest

from app.services.app_deprecation_tracker import AppDeprecationTracker


class TestDeprecate:
    def test_deprecate(self):
        t = AppDeprecationTracker()
        d = t.deprecate("inst-1", "d1", "GET /api/v1/users", "Use v2", "2027-01-01",
                         replacement="GET /api/v2/users", migration_guide_url="https://docs.example.com/migrate")
        assert d.resource == "GET /api/v1/users"
        assert d.replacement == "GET /api/v2/users"

    def test_duplicate(self):
        t = AppDeprecationTracker()
        t.deprecate("inst-1", "d1", "/api/v1", "Old", "2027-01-01")
        with pytest.raises(ValueError, match="already exists"):
            t.deprecate("inst-1", "d1", "/api/v1", "Old2", "2027-06-01")

    def test_missing_sunset(self):
        t = AppDeprecationTracker()
        with pytest.raises(ValueError, match="sunset_date"):
            t.deprecate("inst-1", "d1", "/api", "Old", "")


class TestUsage:
    def test_update(self):
        t = AppDeprecationTracker()
        t.deprecate("inst-1", "d1", "/api/v1", "Old", "2027-01-01")
        d = t.update_usage("inst-1", "d1", usage_count=100, replacement_usage_count=50)
        assert d.usage_count == 100
        assert d.replacement_usage_count == 50


class TestMigrationProgress:
    def test_progress(self):
        t = AppDeprecationTracker()
        t.deprecate("inst-1", "d1", "/api/v1", "Old", "2027-01-01")
        t.update_usage("inst-1", "d1", usage_count=25, replacement_usage_count=75)
        assert t.migration_progress("inst-1", "d1") == 75.0

    def test_no_usage(self):
        t = AppDeprecationTracker()
        t.deprecate("inst-1", "d1", "/api/v1", "Old", "2027-01-01")
        assert t.migration_progress("inst-1", "d1") == 100.0

    def test_zero_migration(self):
        t = AppDeprecationTracker()
        t.deprecate("inst-1", "d1", "/api/v1", "Old", "2027-01-01")
        t.update_usage("inst-1", "d1", usage_count=100, replacement_usage_count=0)
        assert t.migration_progress("inst-1", "d1") == 0.0


class TestList:
    def test_list(self):
        t = AppDeprecationTracker()
        t.deprecate("inst-1", "d1", "/v1", "Old", "2027-01-01")
        t.deprecate("inst-1", "d2", "/v1/auth", "Old", "2027-06-01")
        assert len(t.list_deprecations("inst-1")) == 2


class TestIsolation:
    def test_cross_installation(self):
        t = AppDeprecationTracker()
        t.deprecate("inst-1", "d1", "/v1", "Old", "2027-01-01")
        with pytest.raises(KeyError):
            t.get_deprecation("inst-2", "d1")
