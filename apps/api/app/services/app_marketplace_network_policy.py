"""Network Policy — control outbound network access for sandboxed extensions.

Defines allowlists and denylists for URLs, domains, and ports
that extensions can access from within their sandbox.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import Enum


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"  # allow but log for audit


@dataclass
class NetworkRule:
    rule_id: str
    domain_pattern: str  # glob-style: "*.slack.com", "api.github.com"
    ports: list[int] = field(default_factory=lambda: [443, 80])
    action: PolicyAction = PolicyAction.ALLOW
    protocol: str = "https"


class NetworkPolicy:
    """Manages network access rules for sandboxed extensions."""

    def __init__(self, default_action: PolicyAction = PolicyAction.DENY):
        self._policies: dict[str, list[NetworkRule]] = {}  # ext_id -> rules
        self._default = default_action
        self._access_log: list[dict] = []

    def add_rule(self, extension_id: str, rule: NetworkRule) -> None:
        self._policies.setdefault(extension_id, []).append(rule)

    def remove_rule(self, extension_id: str, rule_id: str) -> bool:
        rules = self._policies.get(extension_id, [])
        before = len(rules)
        self._policies[extension_id] = [r for r in rules if r.rule_id != rule_id]
        return len(self._policies[extension_id]) < before

    def _match_domain(self, pattern: str, domain: str) -> bool:
        """Match domain against glob pattern."""
        regex = pattern.replace(".", r"\.").replace("*", r"[^.]*")
        return bool(re.fullmatch(regex, domain))

    def check_access(self, extension_id: str, domain: str, port: int = 443) -> PolicyAction:
        """Check if an extension is allowed to access a domain:port."""
        rules = self._policies.get(extension_id, [])
        for rule in rules:
            if self._match_domain(rule.domain_pattern, domain) and port in rule.ports:
                self._access_log.append({
                    "extension_id": extension_id, "domain": domain,
                    "port": port, "action": rule.action.value,
                    "rule_id": rule.rule_id,
                })
                return rule.action
        # No matching rule — use default
        self._access_log.append({
            "extension_id": extension_id, "domain": domain,
            "port": port, "action": self._default.value,
            "rule_id": "default",
        })
        return self._default

    def is_allowed(self, extension_id: str, domain: str, port: int = 443) -> bool:
        action = self.check_access(extension_id, domain, port)
        return action in (PolicyAction.ALLOW, PolicyAction.LOG)

    def get_rules(self, extension_id: str) -> list[NetworkRule]:
        return list(self._policies.get(extension_id, []))

    def get_access_log(self, extension_id: str | None = None) -> list[dict]:
        if extension_id:
            return [l for l in self._access_log if l["extension_id"] == extension_id]
        return list(self._access_log)
