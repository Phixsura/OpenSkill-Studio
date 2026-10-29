"""App API Developer API Access Control Matrix — role-based endpoint access."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class AccessRule:
    endpoint: str
    method: str
    allowed_roles: set[str] = field(default_factory=set)
    denied_roles: set[str] = field(default_factory=set)
    public: bool = False

class AppAPIDeveloperAPIApiAccessControlMatrix:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str, str], AccessRule] = {}

    def set_rule(self, installation_id: str, endpoint: str, method: str, allowed_roles: list[str] | None = None, denied_roles: list[str] | None = None, public: bool = False) -> AccessRule:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        r = AccessRule(endpoint=endpoint, method=method.upper(), allowed_roles=set(allowed_roles or []), denied_roles=set(denied_roles or []), public=public)
        if r.allowed_roles & r.denied_roles: raise ValueError("Role cannot be both allowed and denied")
        self._rules[key] = r
        return r

    def check_access(self, installation_id: str, endpoint: str, method: str, role: str) -> bool:
        key = (installation_id, method.upper(), endpoint)
        r = self._rules.get(key)
        if r is None: return False  # default deny
        if r.public: return True
        if role in r.denied_roles: return False
        if r.allowed_roles and role not in r.allowed_roles: return False
        return bool(r.allowed_roles) or r.public

    def accessible_endpoints(self, installation_id: str, role: str) -> list[AccessRule]:
        result = []
        for (inst, _, _), r in self._rules.items():
            if inst == installation_id and (r.public or role in r.allowed_roles):
                result.append(r)
        return result

    def all_rules(self, installation_id: str) -> list[AccessRule]:
        return [r for (inst, _, _), r in self._rules.items() if inst == installation_id]
