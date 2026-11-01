"""Extension Environment Config — manage env-specific configs (dev/staging/prod)."""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class EnvConfig:
    environment: str  # development, staging, production
    values: dict[str, str] = field(default_factory=dict)
    locked: bool = False


class ExtEnvConfigService:
    VALID_ENVS = {"development", "staging", "production"}

    def __init__(self):
        self._configs: dict[str, dict[str, EnvConfig]] = {}  # ext_id -> {env -> config}

    def set(self, extension_id: str, environment: str, key: str, value: str) -> bool:
        if environment not in self.VALID_ENVS:
            raise ValueError(f"Invalid environment: {environment}")
        if extension_id not in self._configs:
            self._configs[extension_id] = {}
        if environment not in self._configs[extension_id]:
            self._configs[extension_id][environment] = EnvConfig(environment=environment)
        cfg = self._configs[extension_id][environment]
        if cfg.locked:
            return False
        cfg.values[key] = value
        return True

    def get(self, extension_id: str, environment: str) -> dict[str, str]:
        return dict(self._configs.get(extension_id, {}).get(environment, EnvConfig(environment)).values)

    def promote(self, extension_id: str, from_env: str, to_env: str) -> bool:
        src = self._configs.get(extension_id, {}).get(from_env)
        if not src: return False
        dst = self._configs[extension_id].get(to_env, EnvConfig(environment=to_env))
        if dst.locked: return False
        dst.values = deepcopy(src.values)
        self._configs[extension_id][to_env] = dst
        return True

    def lock(self, extension_id: str, environment: str) -> bool:
        cfg = self._configs.get(extension_id, {}).get(environment)
        if cfg:
            cfg.locked = True
            return True
        return False

    def diff(self, extension_id: str, env_a: str, env_b: str) -> dict:
        a = self.get(extension_id, env_a)
        b = self.get(extension_id, env_b)
        all_keys = set(a) | set(b)
        return {k: {"a": a.get(k), "b": b.get(k)} for k in all_keys if a.get(k) != b.get(k)}
