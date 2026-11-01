"""Extension IP Allowlist — restrict extension API access by IP."""
from __future__ import annotations
from dataclasses import dataclass, field
import ipaddress
import time


@dataclass
class IpRule:
    rule_id: str
    network: str  # CIDR notation
    description: str = ""
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtIpAllowlistService:
    def __init__(self):
        self._rules: dict[str, list[IpRule]] = {}  # ext_id -> rules
        self._counter = 0

    def add(self, extension_id: str, cidr: str, description: str = "") -> IpRule:
        try:
            ipaddress.ip_network(cidr, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid CIDR: {cidr}") from e
        self._counter += 1
        rule = IpRule(rule_id=f"ip-{self._counter}", network=cidr, description=description)
        if extension_id not in self._rules:
            self._rules[extension_id] = []
        self._rules[extension_id].append(rule)
        return rule

    def check(self, extension_id: str, ip: str) -> bool:
        rules = self._rules.get(extension_id)
        if not rules:
            return True  # no rules = allow all
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(addr in ipaddress.ip_network(r.network, strict=False) for r in rules)

    def remove(self, extension_id: str, rule_id: str) -> bool:
        rules = self._rules.get(extension_id, [])
        for i, r in enumerate(rules):
            if r.rule_id == rule_id:
                rules.pop(i)
                return True
        return False

    def list_rules(self, extension_id: str) -> list[IpRule]:
        return self._rules.get(extension_id, [])
