"""Trace sampling config — configure sampling rules for distributed tracing."""
from __future__ import annotations
import random


class TraceSampler:
    def __init__(self, *, default_rate: float = 0.1):
        self._default_rate = default_rate
        self._rules: list[dict] = []

    def add_rule(self, *, name: str, match_path: str, rate: float) -> dict:
        rate = max(0.0, min(1.0, rate))
        rule = {"name": name, "match_path": match_path, "rate": rate}
        self._rules.append(rule)
        return {"added": name, "rate": rate}

    def should_sample(self, path: str, *, rand_val: float | None = None) -> dict:
        rv = rand_val if rand_val is not None else random.random()
        for rule in self._rules:
            if rule["match_path"] in path:
                sampled = rv < rule["rate"]
                return {"sampled": sampled, "rule": rule["name"], "rate": rule["rate"]}
        sampled = rv < self._default_rate
        return {"sampled": sampled, "rule": "default", "rate": self._default_rate}

    def summary(self) -> dict:
        return {"default_rate": self._default_rate,
                "rules": [{"name": r["name"], "path": r["match_path"],
                           "rate": r["rate"], "rate_display": f"{r['rate'] * 100:.0f}%"}
                          for r in self._rules],
                "total_rules": len(self._rules)}
