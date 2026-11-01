from app.services.app_marketplace_extension_sandbox_env_var import (
    SandboxEnvVarService, EnvScope,
)
import pytest


def test_set_and_get():
    svc = SandboxEnvVarService()
    var = svc.set_var("ext-1", "EXT_API_URL", "https://api.example.com")
    assert var.key == "EXT_API_URL"
    assert var.plain_value == "https://api.example.com"
    assert svc.get_var("ext-1", "EXT_API_URL") is not None


def test_secret_masking():
    svc = SandboxEnvVarService()
    svc.set_var("ext-1", "EXT_TOKEN", "supersecret", is_secret=True)
    listed = svc.list_vars("ext-1")
    assert listed[0]["value"] == "••••••••"
    assert listed[0]["is_secret"] is True


def test_invalid_key():
    svc = SandboxEnvVarService()
    with pytest.raises(ValueError, match="EXT_"):
        svc.set_var("ext-1", "BAD_KEY", "val")


def test_scope_filtering():
    svc = SandboxEnvVarService()
    svc.set_var("ext-1", "EXT_DB", "dev-db", scope=EnvScope.DEV)
    svc.set_var("ext-1", "EXT_LOG", "info", scope=EnvScope.ALL)
    svc.set_var("ext-1", "EXT_PROD_DB", "prod-db", scope=EnvScope.PROD)
    dev_vars = svc.list_vars("ext-1", scope=EnvScope.DEV)
    keys = {v["key"] for v in dev_vars}
    assert "EXT_DB" in keys
    assert "EXT_LOG" in keys
    assert "EXT_PROD_DB" not in keys


def test_resolve_env():
    svc = SandboxEnvVarService()
    svc.set_var("ext-1", "EXT_URL", "http://dev", scope=EnvScope.DEV)
    svc.set_var("ext-1", "EXT_KEY", "secret", is_secret=True, scope=EnvScope.ALL)
    env = svc.resolve_env("ext-1", EnvScope.DEV)
    assert env["EXT_URL"] == "http://dev"
    assert env["EXT_KEY"] == "[SECRET]"


def test_delete():
    svc = SandboxEnvVarService()
    svc.set_var("ext-1", "EXT_TMP", "val")
    assert svc.delete_var("ext-1", "EXT_TMP") is True
    assert svc.get_var("ext-1", "EXT_TMP") is None


def test_bulk_set():
    svc = SandboxEnvVarService()
    count = svc.bulk_set("ext-1", [
        {"key": "EXT_A", "value": "1"},
        {"key": "EXT_B", "value": "2", "is_secret": True},
    ])
    assert count == 2
    assert len(svc.list_vars("ext-1")) == 2


def test_clone_env():
    svc = SandboxEnvVarService()
    svc.set_var("ext-1", "EXT_URL", "http://api")
    svc.set_var("ext-1", "EXT_SECRET", "key", is_secret=True)
    cloned = svc.clone_env("ext-1", "ext-2", exclude_secrets=True)
    assert cloned == 1  # only non-secret
    assert svc.get_var("ext-2", "EXT_URL") is not None
    assert svc.get_var("ext-2", "EXT_SECRET") is None
