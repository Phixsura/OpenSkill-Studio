"""Service mesh traffic policy — manage traffic policies between services."""
from __future__ import annotations


class MeshTrafficPolicy:
    def __init__(self):
        self._policies: dict[str, dict] = {}

    def set_policy(self, source: str, destination: str, timeout_ms: int = 5000,
                   retries: int = 3, circuit_break_threshold: int = 5) -> dict:
        key = f"{source}→{destination}"
        self._policies[key] = {"source": source, "destination": destination,
                                "timeout_ms": timeout_ms, "retries": retries,
                                "circuit_break_threshold": circuit_break_threshold}
        return self._policies[key]

    def get_policy(self, source: str, destination: str) -> dict:
        key = f"{source}→{destination}"
        return self._policies.get(key, {"timeout_ms": 5000, "retries": 3,
                                         "circuit_break_threshold": 5})

    def list_policies(self) -> list[dict]:
        return list(self._policies.values())

    def stats(self) -> dict:
        return {"total_policies": len(self._policies),
                "avg_timeout_ms": round(sum(p["timeout_ms"] for p in self._policies.values()) / max(len(self._policies), 1))}
