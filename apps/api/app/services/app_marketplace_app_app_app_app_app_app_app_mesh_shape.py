"""Mesh traffic shaping — shape traffic between services with delay/abort/rate."""
from __future__ import annotations


def apply_shaping(source: str, destination: str, rules: list[dict]) -> dict:
    effects = []
    for rule in rules:
        if rule.get("source") != source or rule.get("destination") != destination:
            continue
        shape_type = rule["type"]
        if shape_type == "delay":
            effects.append({"type": "delay", "delay_ms": rule.get("delay_ms", 0)})
        elif shape_type == "abort":
            effects.append({"type": "abort", "status": rule.get("status", 503),
                             "percentage": rule.get("percentage", 100)})
        elif shape_type == "rate_limit":
            effects.append({"type": "rate_limit", "rps": rule.get("rps", 100)})
    return {"source": source, "destination": destination, "effects": effects,
            "shaped": len(effects) > 0}


def shaping_summary(rules: list[dict]) -> dict:
    by_type = {}
    for r in rules:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    return {"total_rules": len(rules), "by_type": by_type,
            "active": sum(1 for r in rules if r.get("active", True))}
