"""Tests for App Environment Variable — set, get, mask, delete."""

import pytest

from app.services.app_env_variable import AppEnvVariable


class TestSet:
    def test_set(self):
        e = AppEnvVariable()
        v = e.set("inst-1", "DATABASE_URL", "postgres://localhost/db")
        assert v.key == "DATABASE_URL"

    def test_invalid_key(self):
        e = AppEnvVariable()
        with pytest.raises(ValueError, match="alphanumeric"):
            e.set("inst-1", "BAD KEY!", "value")


class TestGet:
    def test_get(self):
        e = AppEnvVariable()
        e.set("inst-1", "API_KEY", "secret123", sensitive=True)
        v = e.get("inst-1", "API_KEY")
        assert v.value == "secret123"

    def test_not_found(self):
        e = AppEnvVariable()
        with pytest.raises(KeyError):
            e.get("inst-1", "NOPE")


class TestMask:
    def test_sensitive_masked(self):
        e = AppEnvVariable()
        e.set("inst-1", "API_KEY", "secret123456", sensitive=True)
        items = e.list_vars("inst-1")
        masked = [i for i in items if i["key"] == "API_KEY"][0]
        assert "secret" not in masked["value"]
        assert masked["value"].startswith("se")

    def test_non_sensitive_visible(self):
        e = AppEnvVariable()
        e.set("inst-1", "APP_NAME", "myapp")
        items = e.list_vars("inst-1")
        assert items[0]["value"] == "myapp"


class TestEnvironments:
    def test_multi_env(self):
        e = AppEnvVariable()
        e.set("inst-1", "DB", "prod-db", environment="production")
        e.set("inst-1", "DB", "staging-db", environment="staging")
        assert e.environments("inst-1") == ["production", "staging"]
        prod = e.list_vars("inst-1", environment="production")
        assert len(prod) == 1


class TestIsolation:
    def test_cross(self):
        e = AppEnvVariable()
        e.set("inst-1", "KEY", "value")
        assert e.list_vars("inst-2") == []
