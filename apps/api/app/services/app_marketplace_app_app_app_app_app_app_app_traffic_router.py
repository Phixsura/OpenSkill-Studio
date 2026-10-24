"""Traffic router — route traffic with weighted splitting."""
from __future__ import annotations
import hashlib


def create_route(path: str, targets: list[dict]) -> dict:
    total_weight = sum(t.get("weight", 1) for t in targets)
    normalized = []
    for t in targets:
        w = round(t.get("weight", 1) / total_weight * 100, 1)
        normalized.append({"backend": t["backend"], "weight": w})
    return {"path": path, "targets": normalized, "target_count": len(normalized)}


def resolve_target(route: dict, request_id: str) -> str:
    h = int(hashlib.sha256(f"{route['path']}:{request_id}".encode()).hexdigest(), 16)
    pct = (h % 10000) / 100.0
    cumulative = 0.0
    for t in route["targets"]:
        cumulative += t["weight"]
        if pct < cumulative:
            return t["backend"]
    return route["targets"][-1]["backend"]


def build_routing_table(routes: list[dict]) -> dict:
    table = {}
    for r in routes:
        table[r["path"]] = r
    return {"routes": table, "route_count": len(table),
            "paths": sorted(table.keys())}
