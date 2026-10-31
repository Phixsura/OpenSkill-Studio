"""App API Webhook IP Filter — filter webhook delivery by destination IP.

Manages webhook IP filtering:
- Allow/block destination IPs
- Validate before delivery
- Track blocked attempts
- Per-installation scoped filters
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class IPFilterRule:
    """An IP filter rule for webhook destinations."""

    rule_id: str
    cidr: str
    action: str  # "allow" or "block"


class AppAPIWebhookIPFilter:
    """Filter webhook delivery by destination IP."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], IPFilterRule] = {}
        self._blocked_count: dict[str, int] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, cidr: str, action: str,
    ) -> IPFilterRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if action not in ("allow", "block"):
            raise ValueError("action must be allow or block")
        try:
            ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            raise ValueError(f"Invalid CIDR: {cidr}")

        rule = IPFilterRule(rule_id=rule_id, cidr=cidr, action=action)
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def check(self, installation_id: str, ip: str) -> bool:
        """Check if delivery to IP is allowed. Default: allow if no block rules match."""
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False

        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]
        if not rules:
            return True

        for r in rules:
            net = ipaddress.ip_network(r.cidr, strict=False)
            if addr in net:
                if r.action == "block":
                    self._blocked_count[installation_id] = self._blocked_count.get(installation_id, 0) + 1
                    return False
                return True
        return True  # no matching rule = allow

    def blocked_count(self, installation_id: str) -> int:
        return self._blocked_count.get(installation_id, 0)

    def list_rules(self, installation_id: str) -> list[IPFilterRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]
