"""Consumer Environment Manager — multi-environment config with promotion."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

ENV_ORDER = ("development", "staging", "production")


@dataclass
class EnvConfig:
    env_name: str
    consumer_id: str
    variables: dict[str, str] = field(default_factory=dict)
    secrets: dict[str, str] = field(default_factory=dict)
    base_url: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    locked: bool = False


@dataclass
class EnvironmentManager:
    """Manage multi-environment configurations with promotion flow."""

    _envs: dict[str, dict[str, EnvConfig]] = field(default_factory=dict)  # consumer -> {env_name: config}

    def create_env(self, consumer_id: str, env_name: str, base_url: str = "") -> dict:
        if env_name not in ENV_ORDER:
            raise ValueError(f"Invalid environment: {env_name}. Must be one of {ENV_ORDER}")
        envs = self._envs.setdefault(consumer_id, {})
        if env_name in envs:
            raise ValueError(f"Environment {env_name} already exists for {consumer_id}")
        envs[env_name] = EnvConfig(env_name=env_name, consumer_id=consumer_id, base_url=base_url)
        logger.info("env_created", consumer_id=consumer_id, env=env_name)
        return {"consumer_id": consumer_id, "env": env_name}

    def set_variable(self, consumer_id: str, env_name: str, key: str, value: str) -> dict:
        env = self._get_env(consumer_id, env_name)
        if env.locked:
            raise ValueError(f"Environment {env_name} is locked")
        env.variables[key] = value
        return {"env": env_name, "key": key, "set": True}

    def set_secret(self, consumer_id: str, env_name: str, key: str, value: str) -> dict:
        env = self._get_env(consumer_id, env_name)
        if env.locked:
            raise ValueError(f"Environment {env_name} is locked")
        env.secrets[key] = value
        return {"env": env_name, "key": key, "set": True, "masked": True}

    def get_config(self, consumer_id: str, env_name: str, reveal_secrets: bool = False) -> dict:
        env = self._get_env(consumer_id, env_name)
        secrets = {}
        for k, v in env.secrets.items():
            secrets[k] = v if reveal_secrets else f"{'*' * min(len(v), 8)}"
        return {
            "env": env.env_name, "consumer_id": consumer_id,
            "base_url": env.base_url, "variables": dict(env.variables),
            "secrets": secrets, "locked": env.locked,
            "var_count": len(env.variables), "secret_count": len(env.secrets),
        }

    def promote(self, consumer_id: str, from_env: str, to_env: str) -> dict:
        from_idx = ENV_ORDER.index(from_env) if from_env in ENV_ORDER else -1
        to_idx = ENV_ORDER.index(to_env) if to_env in ENV_ORDER else -1
        if from_idx < 0 or to_idx < 0:
            raise ValueError("Invalid environment names")
        if to_idx <= from_idx:
            raise ValueError("Can only promote to a higher environment")
        source = self._get_env(consumer_id, from_env)
        target = self._get_env(consumer_id, to_env)
        if target.locked:
            raise ValueError(f"Target environment {to_env} is locked")
        target.variables = dict(source.variables)
        # Secrets are NOT promoted for security
        logger.info("env_promoted", consumer_id=consumer_id, from_env=from_env, to_env=to_env)
        return {"promoted": True, "from": from_env, "to": to_env,
                "vars_copied": len(target.variables), "secrets_copied": 0}

    def lock(self, consumer_id: str, env_name: str) -> dict:
        env = self._get_env(consumer_id, env_name)
        env.locked = True
        return {"env": env_name, "locked": True}

    def unlock(self, consumer_id: str, env_name: str) -> dict:
        env = self._get_env(consumer_id, env_name)
        env.locked = False
        return {"env": env_name, "locked": False}

    def diff(self, consumer_id: str, env_a: str, env_b: str) -> dict:
        a = self._get_env(consumer_id, env_a)
        b = self._get_env(consumer_id, env_b)
        only_a = sorted(set(a.variables) - set(b.variables))
        only_b = sorted(set(b.variables) - set(a.variables))
        different = [k for k in sorted(set(a.variables) & set(b.variables))
                     if a.variables[k] != b.variables[k]]
        return {"env_a": env_a, "env_b": env_b, "only_in_a": only_a,
                "only_in_b": only_b, "different_values": different}

    def list_envs(self, consumer_id: str) -> list[dict]:
        envs = self._envs.get(consumer_id, {})
        return [{"env": e.env_name, "var_count": len(e.variables),
                 "secret_count": len(e.secrets), "locked": e.locked}
                for e in sorted(envs.values(), key=lambda x: ENV_ORDER.index(x.env_name))]

    def _get_env(self, consumer_id: str, env_name: str) -> EnvConfig:
        envs = self._envs.get(consumer_id, {})
        env = envs.get(env_name)
        if not env:
            raise ValueError(f"Environment {env_name} not found for {consumer_id}")
        return env
