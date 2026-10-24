"""Service dependency matrix — visualize all dependencies as a matrix."""
from __future__ import annotations


def build_matrix(services: list[str], dependencies: dict[str, list[str]]) -> dict:
    matrix = {}
    for svc in services:
        row = {}
        deps = dependencies.get(svc, [])
        for target in services:
            row[target] = target in deps
        matrix[svc] = row
    total_deps = sum(sum(1 for v in row.values() if v) for row in matrix.values())
    density = round(total_deps / max(len(services) ** 2 - len(services), 1) * 100, 1)
    return {"matrix": matrix, "services": services, "total_deps": total_deps,
            "density_pct": density, "service_count": len(services)}


def find_hubs(matrix: dict) -> dict:
    incoming: dict[str, int] = {s: 0 for s in matrix["services"]}
    outgoing: dict[str, int] = {s: 0 for s in matrix["services"]}
    for svc, row in matrix["matrix"].items():
        for target, depends in row.items():
            if depends:
                outgoing[svc] += 1
                incoming[target] += 1
    most_depended = max(incoming, key=incoming.get) if incoming else None
    most_dependent = max(outgoing, key=outgoing.get) if outgoing else None
    return {"most_depended_on": most_depended, "incoming": incoming[most_depended] if most_depended else 0,
            "most_dependent": most_dependent, "outgoing": outgoing[most_dependent] if most_dependent else 0}
