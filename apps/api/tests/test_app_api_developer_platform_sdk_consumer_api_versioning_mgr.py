"""Tests for API Versioning Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_versioning_mgr import (
    VersioningManager,
)


class TestVersioningManager:
    def test_register_and_list(self):
        svc = VersioningManager()
        svc.register("1.0.0")
        svc.register("1.1.0")
        svc.register("2.0.0")
        versions = svc.list_versions()
        assert len(versions) == 3
        assert versions[0]["version"] == "2.0.0"

    def test_get_latest(self):
        svc = VersioningManager()
        svc.register("1.0.0")
        svc.register("2.0.0")
        svc.register("1.5.0")
        latest = svc.get_latest()
        assert latest["version"] == "2.0.0"

    def test_deprecate(self):
        svc = VersioningManager()
        svc.register("1.0.0")
        result = svc.deprecate("1.0.0", sunset_date="2025-06-01")
        assert result["status"] == "deprecated"
        versions = svc.list_versions(status="deprecated")
        assert len(versions) == 1

    def test_sunset(self):
        svc = VersioningManager()
        svc.register("1.0.0")
        svc.sunset("1.0.0")
        assert svc.list_versions(status="sunset")[0]["version"] == "1.0.0"

    def test_latest_excludes_deprecated(self):
        svc = VersioningManager()
        svc.register("1.0.0")
        svc.register("2.0.0")
        svc.deprecate("2.0.0")
        latest = svc.get_latest()
        assert latest["version"] == "1.0.0"

    def test_compatibility_major(self):
        svc = VersioningManager()
        result = svc.check_compatibility("1.0.0", "2.0.0")
        assert result["breaking"] is True
        assert result["level"] == "major"

    def test_compatibility_minor(self):
        svc = VersioningManager()
        result = svc.check_compatibility("1.0.0", "1.1.0")
        assert result["breaking"] is False
        assert result["level"] == "minor"

    def test_migration_path(self):
        svc = VersioningManager()
        svc.register("1.0.0")
        svc.register("1.1.0")
        svc.register("2.0.0")
        path = svc.get_migration_path("1.0.0", "2.0.0")
        assert path == ["1.1.0", "2.0.0"]

    def test_invalid_semver(self):
        svc = VersioningManager()
        with pytest.raises(ValueError):
            svc.register("abc")

    def test_duplicate_version(self):
        svc = VersioningManager()
        svc.register("1.0.0")
        with pytest.raises(ValueError):
            svc.register("1.0.0")

    def test_isolation(self):
        a, b = VersioningManager(), VersioningManager()
        a.register("1.0.0")
        assert b.list_versions() == []
