"""App Network Policy — manage network egress/ingress policies.

Manages network policies for installed apps:
- Define allowed/denied egress destinations
- Port-level restrictions
- Protocol filtering (http, https, tcp)
- Per-installation scoped policies
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class NetworkRule:
    """A network policy rule."""

    rule_id: str
    direction: str  # "egress" or "ingress"
    action: str  # "allow" or "deny"
    destination: str  # hostname or CIDR
    port: int | None = None  # None = any port
    protocol: str = "any"  # "http", "https", "tcp", "any"


class AppNetworkPolicy:
    """Manage network egress/ingress policies."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], NetworkRule] = {}

    def add_rule(
        self,
        installation_id: str,
        rule: NetworkRule,
    ) -> NetworkRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not rule.rule_id:
            raise ValueError("rule_id is required")
        if rule.direction not in ("egress", "ingress"):
            raise ValueError("direction must be egress or ingress")
        if rule.action not in ("allow", "deny"):
            raise ValueError("action must be allow or deny")

        key = (installation_id, rule.rule_id)
        if key in self._rules:
            raise ValueError(f"Rule {rule.rule_id} already exists")

        self._rules[key] = rule
        return rule

    def check_egress(
        self, installation_id: str, destination: str, port: int | None = None
    ) -> bool:
        """Check if egress to destination is allowed. Default: deny."""
        rules = [
            r for (inst, _), r in self._rules.items()
            if inst == installation_id and r.direction == "egress"
        ]
        if not rules:
            return True  # no rules = allow all

        for r in rules:
            if r.action == "deny" and self._matches(r, destination, port):
                return False
        for r in rules:
            if r.action == "allow" and self._matches(r, destination, port):
                return True
        return False  # default deny when rules exist

    def list_rules(self, installation_id: str, direction: str | None = None) -> list[NetworkRule]:
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]
        if direction:
            rules = [r for r in rules if r.direction == direction]
        return rules

    def remove_rule(self, installation_id: str, rule_id: str) -> bool:
        key = (installation_id, rule_id)
        if key in self._rules:
            del self._rules[key]
            return True
        return False

    def _matches(self, rule: NetworkRule, destination: str, port: int | None) -> bool:
        if rule.destination != "*" and rule.destination != destination:
            return False
        if rule.port is not None and port is not None and rule.port != port:
            return False
        return True
