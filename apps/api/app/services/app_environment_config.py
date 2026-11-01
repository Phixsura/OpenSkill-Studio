"""App Environment Config — manage environment-specific settings.

Manages distinct configurations per environment:
- Define environments (dev, staging, prod)
- Per-environment key-value settings
- Promote settings between environments
- Compare settings across environments
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Environment:
    """An environment configuration."""

    env_id: str
    name: str
    settings: dict = field(default_factory=dict)
    locked: bool = False


class AppEnvironmentConfig:
    """Manage environment-specific settings."""

    def __init__(self) -> None:
        # (installation_id, env_id) → Environment
        self._envs: dict[tuple[str, str], Environment] = {}

    def create_environment(
        self,
        installation_id: str,
        env_id: str,
        name: str,
        settings: dict | None = None,
    ) -> Environment:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not env_id:
            raise ValueError("env_id is required")

        key = (installation_id, env_id)
        if key in self._envs:
            raise ValueError(f"Environment {env_id} already exists")

        env = Environment(env_id=env_id, name=name, settings=settings or {})
        self._envs[key] = env
        return env

    def set_value(
        self, installation_id: str, env_id: str, key: str, value: object
    ) -> None:
        env = self._get(installation_id, env_id)
        if env.locked:
            raise ValueError(f"Environment {env_id} is locked")
        env.settings[key] = value

    def get_value(
        self, installation_id: str, env_id: str, key: str, default: object = None
    ) -> object:
        env = self._get(installation_id, env_id)
        return env.settings.get(key, default)

    def get_all(self, installation_id: str, env_id: str) -> dict:
        return dict(self._get(installation_id, env_id).settings)

    def promote(
        self,
        installation_id: str,
        from_env: str,
        to_env: str,
        keys: list[str] | None = None,
    ) -> int:
        """Copy settings from one environment to another. Returns count."""
        source = self._get(installation_id, from_env)
        target = self._get(installation_id, to_env)
        if target.locked:
            raise ValueError(f"Target environment {to_env} is locked")

        to_copy = keys if keys else list(source.settings.keys())
        count = 0
        for k in to_copy:
            if k in source.settings:
                target.settings[k] = source.settings[k]
                count += 1
        return count

    def compare(
        self, installation_id: str, env_a: str, env_b: str
    ) -> dict:
        """Compare settings between two environments."""
        a = self._get(installation_id, env_a)
        b = self._get(installation_id, env_b)
        all_keys = set(a.settings) | set(b.settings)

        diff: dict[str, dict] = {}
        for k in sorted(all_keys):
            va = a.settings.get(k)
            vb = b.settings.get(k)
            if va != vb:
                diff[k] = {"a": va, "b": vb}
        return diff

    def lock(self, installation_id: str, env_id: str) -> None:
        self._get(installation_id, env_id).locked = True

    def unlock(self, installation_id: str, env_id: str) -> None:
        self._get(installation_id, env_id).locked = False

    def list_environments(self, installation_id: str) -> list[Environment]:
        return [e for (inst, _), e in self._envs.items() if inst == installation_id]

    def _get(self, installation_id: str, env_id: str) -> Environment:
        key = (installation_id, env_id)
        env = self._envs.get(key)
        if env is None:
            raise KeyError(f"Environment {env_id} not found")
        return env
