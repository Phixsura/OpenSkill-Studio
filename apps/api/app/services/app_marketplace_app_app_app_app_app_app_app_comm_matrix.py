"""Service communication matrix — map all inter-service communication."""
from __future__ import annotations
from collections import defaultdict


def build_comm_matrix(communications: list[dict]) -> dict:
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    services = set()
    for c in communications:
        src = c["source"]
        dst = c["destination"]
        services.add(src)
        services.add(dst)
        matrix[src][dst] += c.get("count", 1)
    sorted_svcs = sorted(services)
    rows = []
    for src in sorted_svcs:
        row = {"service": src}
        for dst in sorted_svcs:
            row[dst] = matrix[src].get(dst, 0)
        rows.append(row)
    total = sum(sum(d.values()) for d in matrix.values())
    return {"services": sorted_svcs, "rows": rows, "total_communications": total}
