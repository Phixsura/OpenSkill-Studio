"""Endpoint dependency mapper — map which endpoints depend on which services."""
from __future__ import annotations
from collections import defaultdict


def map_endpoint_deps(calls: list[dict]) -> dict:
    by_endpoint: dict[str, set] = defaultdict(set)
    for c in calls:
        ep = c.get("endpoint", "/")
        dep = c.get("downstream_service", "")
        if dep:
            by_endpoint[ep].add(dep)
    results = []
    for ep in sorted(by_endpoint):
        deps = sorted(by_endpoint[ep])
        results.append({"endpoint": ep, "dependencies": deps, "dep_count": len(deps)})
    most_deps = max(results, key=lambda r: r["dep_count"]) if results else None
    return {"endpoints": results, "total": len(results),
            "most_complex": most_deps["endpoint"] if most_deps else "",
            "max_deps": most_deps["dep_count"] if most_deps else 0}
