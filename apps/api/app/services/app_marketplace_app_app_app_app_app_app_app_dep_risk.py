"""Service dependency risk — assess risk from dependency chains."""
from __future__ import annotations


def assess_dependency_risk(service: str, deps: dict[str, dict]) -> dict:
    direct = list(deps.get(service, {}).get("depends_on", []))
    transitive = set()
    queue = list(direct)
    visited = set()
    while queue:
        d = queue.pop(0)
        if d in visited:
            continue
        visited.add(d)
        transitive.add(d)
        queue.extend(deps.get(d, {}).get("depends_on", []))
    depth = _max_depth(service, deps, set())
    risk_score = min(100, len(transitive) * 10 + depth * 15)
    level = "critical" if risk_score >= 70 else "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low"
    return {"service": service, "direct_deps": len(direct), "transitive_deps": len(transitive),
            "max_depth": depth, "risk_score": risk_score, "risk_level": level}


def _max_depth(node: str, deps: dict, visited: set) -> int:
    if node in visited:
        return 0
    visited = visited | {node}
    children = deps.get(node, {}).get("depends_on", [])
    if not children:
        return 0
    return 1 + max(_max_depth(c, deps, visited) for c in children)
