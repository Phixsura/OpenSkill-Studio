"""App Environment Variable — manage app environment variables.

Manages environment variables:
- Store key-value pairs with optional encryption flag
- Mask sensitive values in listings
- Override per environment
- Per-installation scoped variables
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class EnvVariable:
    """An environment variable."""

    key: str
    value: str
    sensitive: bool = False
    environment: str = "production"  # "production", "staging", "development"

    @property
    def masked_value(self) -> str:
        if not self.sensitive:
            return self.value
        if len(self.value) <= 4:
            return "****"
        return self.value[:2] + "*" * (len(self.value) - 4) + self.value[-2:]


class AppEnvVariable:
    """Manage app environment variables."""

    def __init__(self) -> None:
        self._vars: dict[tuple[str, str, str], EnvVariable] = {}

    def set(
        self, installation_id: str, key: str, value: str,
        sensitive: bool = False, environment: str = "production",
    ) -> EnvVariable:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not key:
            raise ValueError("key is required")
        if not key.replace("_", "").replace("-", "").isalnum():
            raise ValueError("key must be alphanumeric (with _ and -)")

        var = EnvVariable(key=key, value=value, sensitive=sensitive, environment=environment)
        self._vars[(installation_id, environment, key)] = var
        return var

    def get(self, installation_id: str, key: str, environment: str = "production") -> EnvVariable:
        k = (installation_id, environment, key)
        var = self._vars.get(k)
        if var is None:
            raise KeyError(f"Variable {key} not found in {environment}")
        return var

    def delete(self, installation_id: str, key: str, environment: str = "production") -> bool:
        k = (installation_id, environment, key)
        if k in self._vars:
            del self._vars[k]
            return True
        return False

    def list_vars(
        self, installation_id: str, environment: str | None = None, mask: bool = True,
    ) -> list[dict]:
        result = []
        for (inst, env, _), var in self._vars.items():
            if inst != installation_id:
                continue
            if environment and env != environment:
                continue
            result.append({
                "key": var.key,
                "value": var.masked_value if mask else var.value,
                "sensitive": var.sensitive,
                "environment": var.environment,
            })
        return sorted(result, key=lambda x: x["key"])

    def environments(self, installation_id: str) -> list[str]:
        envs: set[str] = set()
        for (inst, env, _) in self._vars:
            if inst == installation_id:
                envs.add(env)
        return sorted(envs)
