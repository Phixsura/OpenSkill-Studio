"""Chaos engineering fault injector — simulate failures for resilience testing."""
from __future__ import annotations
import random


class ChaosInjector:
    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._experiments: list[dict] = []

    def inject_latency(self, service: str, min_ms: int, max_ms: int, pct: int = 100) -> dict:
        added_ms = self._rng.randint(min_ms, max_ms) if self._rng.randint(1, 100) <= pct else 0
        exp = {"type": "latency", "service": service, "added_ms": added_ms,
               "active": added_ms > 0}
        self._experiments.append(exp)
        return exp

    def inject_error(self, service: str, error_code: int = 500, pct: int = 50) -> dict:
        triggered = self._rng.randint(1, 100) <= pct
        exp = {"type": "error", "service": service, "error_code": error_code,
               "triggered": triggered}
        self._experiments.append(exp)
        return exp

    def inject_partition(self, from_svc: str, to_svc: str) -> dict:
        exp = {"type": "network_partition", "from": from_svc, "to": to_svc,
               "active": True}
        self._experiments.append(exp)
        return exp

    def summary(self) -> dict:
        active = sum(1 for e in self._experiments if e.get("active") or e.get("triggered"))
        return {"total_experiments": len(self._experiments), "active": active,
                "by_type": {t: sum(1 for e in self._experiments if e["type"] == t)
                            for t in set(e["type"] for e in self._experiments)}}
