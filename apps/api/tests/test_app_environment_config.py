"""Tests for App Environment Config — environments, promote, compare, lock."""

import pytest

from app.services.app_environment_config import AppEnvironmentConfig


class TestCreateEnvironment:
    def test_create(self):
        c = AppEnvironmentConfig()
        e = c.create_environment("inst-1", "prod", "Production", {"db_url": "postgres://prod"})
        assert e.env_id == "prod"
        assert e.settings["db_url"] == "postgres://prod"

    def test_duplicate(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "prod", "Prod")
        with pytest.raises(ValueError, match="already exists"):
            c.create_environment("inst-1", "prod", "Prod 2")


class TestSetGet:
    def test_set_and_get(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "dev", "Dev")
        c.set_value("inst-1", "dev", "debug", True)
        assert c.get_value("inst-1", "dev", "debug") is True

    def test_default(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "dev", "Dev")
        assert c.get_value("inst-1", "dev", "missing", default=42) == 42

    def test_get_all(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "dev", "Dev", {"a": 1, "b": 2})
        assert c.get_all("inst-1", "dev") == {"a": 1, "b": 2}


class TestPromote:
    def test_promote_all(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "staging", "Staging", {"api_key": "stg", "timeout": 30})
        c.create_environment("inst-1", "prod", "Prod")
        count = c.promote("inst-1", "staging", "prod")
        assert count == 2
        assert c.get_value("inst-1", "prod", "api_key") == "stg"

    def test_promote_specific_keys(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "staging", "Staging", {"a": 1, "b": 2, "c": 3})
        c.create_environment("inst-1", "prod", "Prod")
        count = c.promote("inst-1", "staging", "prod", keys=["a", "c"])
        assert count == 2
        assert c.get_value("inst-1", "prod", "b") is None

    def test_promote_to_locked_rejected(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "staging", "Staging", {"x": 1})
        c.create_environment("inst-1", "prod", "Prod")
        c.lock("inst-1", "prod")
        with pytest.raises(ValueError, match="locked"):
            c.promote("inst-1", "staging", "prod")


class TestCompare:
    def test_diff(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "staging", "Staging", {"a": 1, "b": 2})
        c.create_environment("inst-1", "prod", "Prod", {"a": 1, "b": 99, "c": 3})
        diff = c.compare("inst-1", "staging", "prod")
        assert "b" in diff
        assert diff["b"] == {"a": 2, "b": 99}
        assert "c" in diff
        assert "a" not in diff  # same value


class TestLock:
    def test_locked_env_rejects_writes(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "prod", "Prod")
        c.lock("inst-1", "prod")
        with pytest.raises(ValueError, match="locked"):
            c.set_value("inst-1", "prod", "key", "val")

    def test_unlock(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "prod", "Prod")
        c.lock("inst-1", "prod")
        c.unlock("inst-1", "prod")
        c.set_value("inst-1", "prod", "key", "val")
        assert c.get_value("inst-1", "prod", "key") == "val"


class TestIsolation:
    def test_cross_installation(self):
        c = AppEnvironmentConfig()
        c.create_environment("inst-1", "prod", "Prod")
        with pytest.raises(KeyError):
            c.get_all("inst-2", "prod")
