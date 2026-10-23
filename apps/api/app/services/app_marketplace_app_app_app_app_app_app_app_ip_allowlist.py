"""IP allowlist manager — restrict API access by IP address/CIDR."""
from __future__ import annotations
import ipaddress


class IpAllowlistManager:
    def __init__(self):
        self._rules: list[dict] = []

    def add_rule(self, *, cidr: str, label: str = "", enabled: bool = True) -> dict:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except ValueError as e:
            return {"error": f"Invalid CIDR: {e}"}
        rule = {"cidr": str(network), "label": label, "enabled": enabled,
                "version": network.version, "hosts": network.num_addresses}
        self._rules.append(rule)
        return {"added": str(network), "label": label, "hosts": network.num_addresses}

    def check_ip(self, ip: str) -> dict:
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return {"allowed": False, "reason": "invalid_ip"}
        if not self._rules:
            return {"allowed": True, "reason": "no_rules"}
        enabled_rules = [r for r in self._rules if r["enabled"]]
        if not enabled_rules:
            return {"allowed": True, "reason": "all_disabled"}
        for r in enabled_rules:
            if addr in ipaddress.ip_network(r["cidr"], strict=False):
                return {"allowed": True, "matched_rule": r["cidr"], "label": r["label"]}
        return {"allowed": False, "reason": "not_in_allowlist"}

    def list_rules(self) -> list[dict]:
        return list(self._rules)

    def remove_rule(self, cidr: str) -> dict:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r["cidr"] != cidr]
        return {"removed": before > len(self._rules)}
