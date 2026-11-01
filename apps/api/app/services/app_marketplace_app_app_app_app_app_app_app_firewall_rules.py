"""Network firewall rules — manage inbound/outbound firewall rules."""
from __future__ import annotations
import ipaddress


def create_rule(name: str, direction: str, action: str, protocol: str,
                 port: int, source: str = "0.0.0.0/0") -> dict:
    try:
        ipaddress.ip_network(source, strict=False)
    except ValueError:
        return {"created": False, "error": "invalid_source_cidr"}
    return {"created": True, "name": name, "direction": direction,
            "action": action, "protocol": protocol.lower(),
            "port": port, "source": source, "priority": 100}


def evaluate_rules(rules: list[dict], direction: str, port: int, src_ip: str) -> dict:
    for r in sorted(rules, key=lambda x: x.get("priority", 100)):
        if r["direction"] != direction:
            continue
        if r["port"] != 0 and r["port"] != port:
            continue
        try:
            if ipaddress.ip_address(src_ip) in ipaddress.ip_network(r["source"], strict=False):
                return {"matched": True, "rule": r["name"], "action": r["action"]}
        except ValueError:
            continue
    return {"matched": False, "action": "deny"}  # default deny


def firewall_summary(rules: list[dict]) -> dict:
    allow_count = sum(1 for r in rules if r["action"] == "allow")
    deny_count = sum(1 for r in rules if r["action"] == "deny")
    return {"total": len(rules), "allow": allow_count, "deny": deny_count,
            "by_direction": {"ingress": sum(1 for r in rules if r["direction"] == "ingress"),
                             "egress": sum(1 for r in rules if r["direction"] == "egress")}}
