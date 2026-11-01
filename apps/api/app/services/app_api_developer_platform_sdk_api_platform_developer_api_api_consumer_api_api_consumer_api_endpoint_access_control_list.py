"""Endpoint Access Control List — per-endpoint allow/deny lists for consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ACLRule:
    rule_id: str
    endpoint_path: str
    consumer_id: str
    action: str = "allow"  # "allow" or "deny"
    reason: str = ""

@dataclass
class ACLCheckResult:
    allowed: bool
    matched_rule: ACLRule | None = None
    reason: str = "default_allow"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList:
    def __init__(self, default_policy: str = "allow") -> None:
        self._rules: dict[tuple[str, str], list[ACLRule]] = {}  # (inst, path) -> rules
        self._default = default_policy  # "allow" or "deny"

    def add_rule(self, installation_id: str, rule: ACLRule) -> ACLRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if rule.action not in ("allow", "deny"):
            raise ValueError("action must be 'allow' or 'deny'")
        key = (installation_id, rule.endpoint_path)
        if key not in self._rules:
            self._rules[key] = []
        # Check duplicate
        for existing in self._rules[key]:
            if existing.consumer_id == rule.consumer_id:
                raise ValueError(f"Rule for consumer {rule.consumer_id} already exists on {rule.endpoint_path}")
        self._rules[key].append(rule)
        log.info("acl_rule_added", installation_id=installation_id, path=rule.endpoint_path, consumer=rule.consumer_id, action=rule.action)
        return rule

    def remove_rule(self, installation_id: str, endpoint_path: str, consumer_id: str) -> None:
        key = (installation_id, endpoint_path)
        rules = self._rules.get(key, [])
        self._rules[key] = [r for r in rules if r.consumer_id != consumer_id]

    def check(self, installation_id: str, endpoint_path: str, consumer_id: str) -> ACLCheckResult:
        rules = self._rules.get((installation_id, endpoint_path), [])
        # Deny rules evaluated first (deny takes precedence)
        for r in rules:
            if r.consumer_id == consumer_id and r.action == "deny":
                return ACLCheckResult(allowed=False, matched_rule=r, reason="explicit_deny")
        for r in rules:
            if r.consumer_id == consumer_id and r.action == "allow":
                return ACLCheckResult(allowed=True, matched_rule=r, reason="explicit_allow")
        # Default policy
        return ACLCheckResult(allowed=(self._default == "allow"), reason=f"default_{self._default}")

    def list_rules(self, installation_id: str, endpoint_path: str | None = None) -> list[ACLRule]:
        if endpoint_path:
            return self._rules.get((installation_id, endpoint_path), [])
        return [r for (inst, _), rules in self._rules.items() if inst == installation_id for r in rules]
