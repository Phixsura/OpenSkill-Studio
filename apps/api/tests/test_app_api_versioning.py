"""Tests for App API Versioning — register, lifecycle, active listing."""

import pytest

from app.services.app_api_versioning import AppAPIVersioning, VersionStatus


class TestRegister:
    def test_register(self):
        v = AppAPIVersioning()
        ver = v.register("inst-1", "v2", endpoint_count=15)
        assert ver.status == VersionStatus.DRAFT

    def test_duplicate(self):
        v = AppAPIVersioning()
        v.register("inst-1", "v2")
        with pytest.raises(ValueError, match="already registered"):
            v.register("inst-1", "v2")


class TestLifecycle:
    def test_activate(self):
        v = AppAPIVersioning()
        v.register("inst-1", "v2")
        ver = v.activate("inst-1", "v2")
        assert ver.status == VersionStatus.ACTIVE

    def test_deprecate(self):
        v = AppAPIVersioning()
        v.register("inst-1", "v1")
        v.activate("inst-1", "v1")
        ver = v.deprecate("inst-1", "v1")
        assert ver.status == VersionStatus.DEPRECATED

    def test_sunset(self):
        v = AppAPIVersioning()
        v.register("inst-1", "v1")
        v.activate("inst-1", "v1")
        v.deprecate("inst-1", "v1")
        ver = v.sunset("inst-1", "v1")
        assert ver.status == VersionStatus.SUNSET


class TestQuery:
    def test_active(self):
        v = AppAPIVersioning()
        v.register("inst-1", "v1")
        v.activate("inst-1", "v1")
        v.register("inst-1", "v2")
        assert len(v.active_versions("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        v = AppAPIVersioning()
        v.register("inst-1", "v1")
        assert v.list_versions("inst-2") == []
