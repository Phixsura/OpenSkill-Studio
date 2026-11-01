"""API Consumer Environment Variable — manage per-consumer environment config."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class EnvVar:
    key: str
    value: str
    secret: bool = False  # if True, value is masked
    description: str = ""

_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariable:
    def __init__(self) -> None:
        self._vars: dict[tuple[str, str, str], EnvVar] = {}

    def set_var(self, installation_id: str, consumer_id: str, var: EnvVar) -> EnvVar:
        if not installation_id: raise ValueError("installation_id is required")
        if not _KEY_RE.match(var.key): raise ValueError(f"Invalid key: {var.key} (must be UPPER_SNAKE_CASE)")
        if var.secret and len(var.value) < 8: raise ValueError("Secret values must be >= 8 chars")
        self._vars[(installation_id, consumer_id, var.key)] = var
        return var

    def get_var(self, installation_id: str, consumer_id: str, key: str) -> EnvVar | None:
        var = self._vars.get((installation_id, consumer_id, key))
        if var and var.secret:
            return EnvVar(key=var.key, value="***" + var.value[-4:], secret=True, description=var.description)
        return var

    def delete_var(self, installation_id: str, consumer_id: str, key: str) -> bool:
        k = (installation_id, consumer_id, key)
        if k in self._vars: del self._vars[k]; return True
        return False

    def list_vars(self, installation_id: str, consumer_id: str) -> list[EnvVar]:
        result = []
        for (inst, cid, _), var in self._vars.items():
            if inst == installation_id and cid == consumer_id:
                if var.secret:
                    result.append(EnvVar(key=var.key, value="***" + var.value[-4:], secret=True, description=var.description))
                else:
                    result.append(var)
        return result

    def var_count(self, installation_id: str, consumer_id: str) -> int:
        return sum(1 for (inst, cid, _) in self._vars if inst == installation_id and cid == consumer_id)
