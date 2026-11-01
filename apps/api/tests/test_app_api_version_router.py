"""Tests for App API Version Router — registration, resolve, sunset."""

import pytest

from app.services.app_api_version_router import AppAPIVersionRouter, VersionStatus


class TestRegister:
    def test_register(self):
        r = AppAPIVersionRouter()
        v = r.register_version("inst-1", "v2", "/api/v2")
        assert v.version == "v2"
        assert v.status == VersionStatus.ACTIVE

    def test_duplicate(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v1", "/api/v1")
        with pytest.raises(ValueError, match="already registered"):
            r.register_version("inst-1", "v1", "/api/v1")


class TestResolve:
    def test_explicit_version(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v2", "/api/v2")
        v = r.resolve("inst-1", "v2")
        assert v.base_path == "/api/v2"

    def test_default_version(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v2", "/api/v2")
        r.set_default("inst-1", "v2")
        v = r.resolve("inst-1")
        assert v.version == "v2"

    def test_no_default(self):
        r = AppAPIVersionRouter()
        with pytest.raises(ValueError, match="No version"):
            r.resolve("inst-1")

    def test_sunset_blocked(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v1", "/api/v1", status=VersionStatus.SUNSET)
        with pytest.raises(ValueError, match="sunset"):
            r.resolve("inst-1", "v1")

    def test_deprecated_allowed(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v1", "/api/v1", status=VersionStatus.DEPRECATED)
        v = r.resolve("inst-1", "v1")
        assert v.status == VersionStatus.DEPRECATED

    def test_unknown_version(self):
        r = AppAPIVersionRouter()
        with pytest.raises(KeyError):
            r.resolve("inst-1", "v99")


class TestListing:
    def test_list_all(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v1", "/api/v1", status=VersionStatus.SUNSET)
        r.register_version("inst-1", "v2", "/api/v2")
        assert len(r.list_versions("inst-1")) == 2

    def test_active_only(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v1", "/api/v1", status=VersionStatus.SUNSET)
        r.register_version("inst-1", "v2", "/api/v2")
        assert len(r.get_active_versions("inst-1")) == 1


class TestIsolation:
    def test_cross_installation(self):
        r = AppAPIVersionRouter()
        r.register_version("inst-1", "v1", "/api/v1")
        with pytest.raises(KeyError):
            r.resolve("inst-2", "v1")
