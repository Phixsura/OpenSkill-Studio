"""Service mesh policy — manage traffic policies between services."""
from __future__ import annotations


def create_traffic_policy(name: str, source: str, destination: str,
                            timeout_ms: int = 30000, retries: int = 3,
                            circuit_breaker: bool = False) -> dict:
    return {"name": name, "source": source, "destination": destination,
            "timeout_ms": timeout_ms, "retries": retries,
            "circuit_breaker": circuit_breaker}


def evaluate_mesh_policies(policies: list[dict]) -> dict:
    by_source: dict[str, int] = {}
    by_dest: dict[str, int] = {}
    with_cb = 0
    for p in policies:
        by_source[p["source"]] = by_source.get(p["source"], 0) + 1
        by_dest[p["destination"]] = by_dest.get(p["destination"], 0) + 1
        if p.get("circuit_breaker"):
            with_cb += 1
    return {"total_policies": len(policies), "by_source": by_source,
            "by_destination": by_dest, "with_circuit_breaker": with_cb,
            "cb_coverage_pct": round(with_cb / max(len(policies), 1) * 100)}
