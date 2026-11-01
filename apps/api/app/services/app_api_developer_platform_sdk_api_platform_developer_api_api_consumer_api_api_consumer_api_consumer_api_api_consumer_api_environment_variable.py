"""Consumer API Environment Variable — manage environment-specific config variables."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class EnvVariable:
    key: str
    value: str
    environment: str = "production"  # "production", "staging", "development"
    sensitive: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable:
    def __init__(self) -> None:
        self._vars: dict[tuple[str, str, str, str], EnvVariable] = {}  # (inst, consumer, env, key)

    def set_variable(self, installation_id: str, consumer_id: str, var: EnvVariable, now: datetime | None = None) -> EnvVariable:
        if not installation_id:
            raise ValueError("installation_id is required")
        if var.environment not in ("production", "staging", "development"):
            raise ValueError(f"Invalid environment: {var.environment}")
        if not var.key or not var.key.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Key must be alphanumeric with underscores/hyphens")
        now = now or datetime.utcnow()
        key = (installation_id, consumer_id, var.environment, var.key)
        existing = self._vars.get(key)
        if existing:
            var.created_at = existing.created_at
        else:
            var.created_at = now
        var.updated_at = now
        self._vars[key] = var
        return var

    def get_variable(self, installation_id: str, consumer_id: str, environment: str, key: str) -> EnvVariable | None:
        v = self._vars.get((installation_id, consumer_id, environment, key))
        if v and v.sensitive:
            # Return masked value for sensitive vars
            return EnvVariable(key=v.key, value="***", environment=v.environment, sensitive=True, created_at=v.created_at, updated_at=v.updated_at)
        return v

    def delete_variable(self, installation_id: str, consumer_id: str, environment: str, key: str) -> None:
        k = (installation_id, consumer_id, environment, key)
        if k not in self._vars:
            raise ValueError("Variable not found")
        del self._vars[k]

    def list_variables(self, installation_id: str, consumer_id: str, environment: str) -> list[EnvVariable]:
        result = []
        for (inst, cid, env, _), v in self._vars.items():
            if inst == installation_id and cid == consumer_id and env == environment:
                if v.sensitive:
                    result.append(EnvVariable(key=v.key, value="***", environment=v.environment, sensitive=True, created_at=v.created_at, updated_at=v.updated_at))
                else:
                    result.append(v)
        return sorted(result, key=lambda v: v.key)

    def copy_to_environment(self, installation_id: str, consumer_id: str, from_env: str, to_env: str, now: datetime | None = None) -> int:
        now = now or datetime.utcnow()
        copied = 0
        for (inst, cid, env, key), v in list(self._vars.items()):
            if inst == installation_id and cid == consumer_id and env == from_env:
                new_var = EnvVariable(key=v.key, value=v.value, environment=to_env, sensitive=v.sensitive, created_at=now, updated_at=now)
                self._vars[(installation_id, consumer_id, to_env, key)] = new_var
                copied += 1
        return copied
