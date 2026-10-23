"""Traffic shaper — control traffic distribution with weighted routing rules."""
from __future__ import annotations
import hashlib


class TrafficShaper:
    def __init__(self):
        self._rules: list[dict] = []

    def add_rule(self, *, name: str, target: str, weight: int,
                  match_header: str | None = None, match_value: str | None = None) -> dict:
        rule = {"name": name, "target": target, "weight": weight,
                "match_header": match_header, "match_value": match_value}
        self._rules.append(rule)
        return {"added": name, "target": target, "weight": weight}

    def route(self, *, headers: dict | None = None, user_id: str = "") -> dict:
        hdrs = headers or {}
        # Check header-based rules first
        for r in self._rules:
            if r["match_header"] and r["match_value"]:
                if hdrs.get(r["match_header"]) == r["match_value"]:
                    return {"target": r["target"], "rule": r["name"], "reason": "header_match"}
        # Fall back to weighted routing
        weighted = [r for r in self._rules if not r["match_header"]]
        if not weighted:
            return {"target": "default", "rule": None, "reason": "no_rules"}
        total_weight = sum(r["weight"] for r in weighted)
        h = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16) if user_id else 0
        bucket = h % max(total_weight, 1)
        cumulative = 0
        for r in weighted:
            cumulative += r["weight"]
            if bucket < cumulative:
                return {"target": r["target"], "rule": r["name"], "reason": "weighted"}
        return {"target": weighted[-1]["target"], "rule": weighted[-1]["name"], "reason": "weighted"}

    def distribution(self) -> dict:
        weighted = [r for r in self._rules if not r["match_header"]]
        total = sum(r["weight"] for r in weighted)
        return {"rules": [{"name": r["name"], "target": r["target"], "weight": r["weight"],
                           "pct": round(r["weight"] / max(total, 1) * 100, 1)}
                          for r in weighted], "total_weight": total}
