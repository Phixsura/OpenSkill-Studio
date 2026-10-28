"""App IP Allow List — IP-based access control for installed apps.

Manages IP allowlists and denylists:
- Add/remove IP addresses and CIDR ranges
- Check if an IP is allowed
- Support for both allowlist and denylist modes
- Per-installation scoped rules
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class IPRule:
    """An IP access rule."""

    rule_id: str
    network: str  # IP or CIDR
    description: str = ""
    _parsed: ipaddress.IPv4Network | ipaddress.IPv6Network | None = field(
        default=None, repr=False, compare=False,
    )


class AppIPAllowList:
    """IP-based access control for installed apps."""

    def __init__(self, mode: str = "allowlist") -> None:
        if mode not in ("allowlist", "denylist"):
            raise ValueError("mode must be 'allowlist' or 'denylist'")
        self._mode = mode
        # installation_id → list[IPRule]
        self._rules: dict[str, list[IPRule]] = {}

    @property
    def mode(self) -> str:
        return self._mode

    def add_rule(
        self,
        installation_id: str,
        rule_id: str,
        network: str,
        description: str = "",
    ) -> IPRule:
        """Add an IP or CIDR rule."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not rule_id:
            raise ValueError("rule_id is required")

        # Validate network
        try:
            parsed = ipaddress.ip_network(network, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid network: {network}") from e

        rules = self._rules.setdefault(installation_id, [])
        for r in rules:
            if r.rule_id == rule_id:
                raise ValueError(f"Rule {rule_id} already exists")

        rule = IPRule(
            rule_id=rule_id,
            network=str(parsed),
            description=description,
            _parsed=parsed,
        )
        rules.append(rule)
        return rule

    def remove_rule(self, installation_id: str, rule_id: str) -> bool:
        """Remove a rule. Returns True if found."""
        rules = self._rules.get(installation_id, [])
        before = len(rules)
        self._rules[installation_id] = [r for r in rules if r.rule_id != rule_id]
        return len(self._rules[installation_id]) < before

    def check_ip(self, installation_id: str, ip: str) -> bool:
        """Check if an IP is allowed. Returns True if access is granted."""
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False

        rules = self._rules.get(installation_id, [])

        if self._mode == "allowlist":
            if not rules:
                return True  # no rules = allow all
            return any(self._matches(r, addr) for r in rules)
        else:  # denylist
            return not any(self._matches(r, addr) for r in rules)

    def list_rules(self, installation_id: str) -> list[IPRule]:
        return list(self._rules.get(installation_id, []))

    def _matches(self, rule: IPRule, addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        if rule._parsed is None:
            try:
                rule._parsed = ipaddress.ip_network(rule.network, strict=False)
            except ValueError:
                return False
        return addr in rule._parsed
