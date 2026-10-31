"""Tests for Consumer Environment Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_env_manager import EnvironmentManager


class TestEnvironmentManager:
    def _setup(self):
        svc = EnvironmentManager()
        svc.create_env("c1", "development", "http://dev.api.com")
        svc.create_env("c1", "staging", "http://staging.api.com")
        svc.create_env("c1", "production", "http://api.com")
        return svc

    def test_create_and_list(self):
        svc = self._setup()
        envs = svc.list_envs("c1")
        assert len(envs) == 3
        assert envs[0]["env"] == "development"

    def test_set_variable(self):
        svc = self._setup()
        svc.set_variable("c1", "development", "API_KEY", "dev-key-123")
        config = svc.get_config("c1", "development")
        assert config["variables"]["API_KEY"] == "dev-key-123"

    def test_secrets_masked(self):
        svc = self._setup()
        svc.set_secret("c1", "development", "DB_PASS", "super-secret")
        config = svc.get_config("c1", "development", reveal_secrets=False)
        assert "super-secret" not in config["secrets"]["DB_PASS"]
        config_revealed = svc.get_config("c1", "development", reveal_secrets=True)
        assert config_revealed["secrets"]["DB_PASS"] == "super-secret"

    def test_promote(self):
        svc = self._setup()
        svc.set_variable("c1", "development", "VERSION", "2.0")
        svc.set_secret("c1", "development", "KEY", "secret")
        result = svc.promote("c1", "development", "staging")
        assert result["vars_copied"] == 1
        assert result["secrets_copied"] == 0
        config = svc.get_config("c1", "staging")
        assert config["variables"]["VERSION"] == "2.0"

    def test_promote_wrong_direction(self):
        svc = self._setup()
        with pytest.raises(ValueError):
            svc.promote("c1", "production", "development")

    def test_lock(self):
        svc = self._setup()
        svc.lock("c1", "production")
        with pytest.raises(ValueError):
            svc.set_variable("c1", "production", "X", "Y")

    def test_unlock(self):
        svc = self._setup()
        svc.lock("c1", "production")
        svc.unlock("c1", "production")
        svc.set_variable("c1", "production", "X", "Y")
        assert svc.get_config("c1", "production")["variables"]["X"] == "Y"

    def test_diff(self):
        svc = self._setup()
        svc.set_variable("c1", "development", "A", "1")
        svc.set_variable("c1", "development", "B", "2")
        svc.set_variable("c1", "staging", "A", "1")
        svc.set_variable("c1", "staging", "C", "3")
        diff = svc.diff("c1", "development", "staging")
        assert "B" in diff["only_in_a"]
        assert "C" in diff["only_in_b"]

    def test_invalid_env(self):
        svc = EnvironmentManager()
        with pytest.raises(ValueError):
            svc.create_env("c1", "test")

    def test_duplicate_env(self):
        svc = self._setup()
        with pytest.raises(ValueError):
            svc.create_env("c1", "development")

    def test_isolation(self):
        a, b = EnvironmentManager(), EnvironmentManager()
        a.create_env("c1", "development")
        assert b.list_envs("c1") == []
