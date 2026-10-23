"""Network policy — define egress/ingress rules for sandboxed apps."""

import re

DOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?(\.[a-z]{2,})+$")


def create_network_policy(*, app_id: str, rules: list[dict]) -> dict:
    validated = []
    errors = []
    for i, rule in enumerate(rules):
        direction = rule.get("direction", "egress")
        if direction not in ("egress", "ingress"):
            errors.append(f"Rule {i}: invalid direction '{direction}'")
            continue
        target = rule.get("target", "")
        port = rule.get("port")
        protocol = rule.get("protocol", "tcp")
        if target != "*" and not DOMAIN_RE.match(target.lower()):
            errors.append(f"Rule {i}: invalid target '{target}'")
            continue
        validated.append({
            "direction": direction,
            "target": target.lower() if target != "*" else "*",
            "port": port,
            "protocol": protocol,
            "action": rule.get("action", "allow"),
        })
    return {
        "app_id": app_id,
        "rules": validated,
        "errors": errors,
        "valid": len(errors) == 0,
        "egress_count": sum(1 for r in validated if r["direction"] == "egress"),
        "ingress_count": sum(1 for r in validated if r["direction"] == "ingress"),
    }
