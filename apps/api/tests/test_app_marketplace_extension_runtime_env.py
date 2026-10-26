from app.services.app_marketplace_extension_runtime_env import (
    RuntimeEnvService, EnvState,
)
import pytest


def test_create_env():
    svc = RuntimeEnvService()
    env = svc.create("ext-1", "node20", entrypoint="main.js")
    assert env.env_id.startswith("env_")
    assert env.runtime == "node20"
    assert env.state == EnvState.CREATED


def test_unsupported_runtime():
    svc = RuntimeEnvService()
    with pytest.raises(ValueError, match="Unsupported runtime"):
        svc.create("ext-1", "ruby3.2")


def test_forbidden_env_var():
    svc = RuntimeEnvService()
    with pytest.raises(ValueError, match="Forbidden env var"):
        svc.create("ext-1", "node18", env_vars={"AWS_SECRET": "x"})


def test_lifecycle():
    svc = RuntimeEnvService()
    env = svc.create("ext-1", "python3.12")
    r = svc.start(env.env_id)
    assert r["ok"] is True
    assert env.state == EnvState.RUNNING
    r2 = svc.stop(env.env_id)
    assert r2["ok"] is True
    assert env.state == EnvState.STOPPED


def test_cannot_start_running():
    svc = RuntimeEnvService()
    env = svc.create("ext-1", "deno")
    svc.start(env.env_id)
    r = svc.start(env.env_id)
    assert r["ok"] is False


def test_destroy():
    svc = RuntimeEnvService()
    env = svc.create("ext-1", "bun")
    svc.start(env.env_id)
    assert svc.destroy(env.env_id) is True
    assert env.state == EnvState.DESTROYED
    assert svc.list_envs("ext-1") == []


def test_resource_limits_clamped():
    svc = RuntimeEnvService()
    env = svc.create("ext-1", "node18", limits={"cpu_cores": 99, "memory_mb": 9999})
    assert env.limits.cpu_cores == 4.0
    assert env.limits.memory_mb == 2048
