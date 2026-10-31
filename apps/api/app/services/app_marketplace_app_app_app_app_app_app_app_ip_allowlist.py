"""IP allowlist manager — manage IP-based access control lists."""
from __future__ import annotations
import ipaddress


class IpAllowlist:
    def __init__(self):
        self._rules: list[dict] = []

    def add_rule(self, name: str, cidr: str, description: str = "") -> dict:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except ValueError as e:
            return {"added": False, "error": str(e)}
        self._rules.append({"name": name, "cidr": cidr, "network": network,
                             "description": description})
        return {"added": True, "name": name, "cidr": cidr}

    def check(self, ip_str: str) -> dict:
        try:
            addr = ipaddress.ip_address(ip_str)
        except ValueError:
            return {"allowed": False, "reason": "invalid_ip"}
        for rule in self._rules:
            if addr in rule["network"]:
                return {"allowed": True, "matched_rule": rule["name"], "cidr": rule["cidr"]}
        return {"allowed": False, "reason": "no_matching_rule"}

    def remove_rule(self, name: str) -> dict:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r["name"] != name]
        return {"removed": before != len(self._rules), "name": name}

    def list_rules(self) -> list[dict]:
        return [{"name": r["name"], "cidr": r["cidr"], "description": r["description"]}
                for r in self._rules]
