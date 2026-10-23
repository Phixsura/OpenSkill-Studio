"""Network policy manager — define ingress/egress rules."""
from __future__ import annotations
import ipaddress


ACTIONS = {"allow", "deny"}
DIRECTIONS = {"ingress", "egress"}


def create_rule(name: str, direction: str, action: str, source: str,
                destination: str, port: int, protocol: str = "tcp") -> dict:
    if direction not in DIRECTIONS:
        return {"created": False, "error": "invalid_direction"}
    if action not in ACTIONS:
        return {"created": False, "error": "invalid_action"}
    return {"created": True, "name": name, "direction": direction,
            "action": action, "source": source, "destination": destination,
            "port": port, "protocol": protocol.lower(), "priority": 100}


def evaluate_traffic(rules: list[dict], direction: str, src: str,
                     dst: str, port: int) -> dict:
    for r in sorted(rules, key=lambda x: x.get("priority", 100)):
        if r["direction"] != direction:
            continue
        src_match = r["source"] == "*" or r["source"] == src
        dst_match = r["destination"] == "*" or r["destination"] == dst
        port_match = r["port"] == 0 or r["port"] == port
        if src_match and dst_match and port_match:
            return {"allowed": r["action"] == "allow", "matched_rule": r["name"]}
    return {"allowed": True, "matched_rule": "default_allow"}
