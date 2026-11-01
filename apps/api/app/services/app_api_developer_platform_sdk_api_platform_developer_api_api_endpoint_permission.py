"""API Endpoint Permission — fine-grained endpoint access control."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PermissionRule:
    rule_id: str
    endpoint: str
    method: str
    required_scopes: list[str] = field(default_factory=list)
    required_roles: list[str] = field(default_factory=list)
    public: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermission:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str, str], PermissionRule] = {}

    def set_rule(self, installation_id: str, rule: PermissionRule) -> PermissionRule:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, rule.method.upper(), rule.endpoint)
        rule.method = rule.method.upper()
        self._rules[key] = rule
        return rule

    def check_access(self, installation_id: str, method: str, endpoint: str, scopes: list[str] | None = None, roles: list[str] | None = None) -> dict[str, object]:
        key = (installation_id, method.upper(), endpoint)
        rule = self._rules.get(key)
        if rule is None: return {"allowed": False, "reason": "no_rule"}
        if rule.public: return {"allowed": True, "reason": "public"}
        consumer_scopes = set(scopes or [])
        consumer_roles = set(roles or [])
        if rule.required_scopes and not consumer_scopes.intersection(rule.required_scopes):
            return {"allowed": False, "reason": "missing_scope", "required": rule.required_scopes}
        if rule.required_roles and not consumer_roles.intersection(rule.required_roles):
            return {"allowed": False, "reason": "missing_role", "required": rule.required_roles}
        return {"allowed": True, "reason": "authorized"}

    def list_rules(self, installation_id: str) -> list[PermissionRule]:
        return [r for (inst, _, _), r in self._rules.items() if inst == installation_id]

    def public_endpoints(self, installation_id: str) -> list[PermissionRule]:
        return [r for (inst, _, _), r in self._rules.items() if inst == installation_id and r.public]
