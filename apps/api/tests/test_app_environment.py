"""App environment config tests."""
import pytest
from app.services.app_environment import build_sandbox_env, validate_env_keys, RESERVED_ENV_VARS

def test_basic_env():
    env = build_sandbox_env(app_id="a1", installation_id="i1", org_id="o1", function_name="fn")
    assert env["OPENSKILL_APP_ID"] == "a1"
    assert env["OPENSKILL_SANDBOX"] == "1"

def test_secrets_injected():
    env = build_sandbox_env(app_id="a", installation_id="i", org_id="o", function_name="f",
                            secrets={"api_key": "secret123"})
    assert env["OPENSKILL_SECRET_API_KEY"] == "secret123"

def test_config_injected():
    env = build_sandbox_env(app_id="a", installation_id="i", org_id="o", function_name="f",
                            config={"base_url": "https://api.com"})
    assert env["OPENSKILL_CONFIG_BASE_URL"] == "https://api.com"

def test_no_secrets():
    env = build_sandbox_env(app_id="a", installation_id="i", org_id="o", function_name="f")
    secret_keys = [k for k in env if k.startswith("OPENSKILL_SECRET_")]
    assert len(secret_keys) == 0

def test_validate_no_conflicts():
    assert validate_env_keys(["MY_VAR", "CUSTOM"]) == []

def test_validate_conflicts():
    conflicts = validate_env_keys(["OPENSKILL_APP_ID", "MY_VAR"])
    assert "OPENSKILL_APP_ID" in conflicts

def test_reserved_count():
    assert len(RESERVED_ENV_VARS) >= 5
