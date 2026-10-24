"""Fleet health matrix — cross-dimensional platform health view."""
from __future__ import annotations
def fleet_health_matrix(dims: dict) -> dict:
    values = list(dims.values())
    avg = round(sum(values) / max(len(values), 1), 1)
    weakest = min(dims, key=lambda k: dims[k]) if dims else None
    strongest = max(dims, key=lambda k: dims[k]) if dims else None
    return {"dimensions": len(dims), "avg_score": avg, "weakest": weakest,
            "strongest": strongest, "balanced": max(values) - min(values) <= 20 if values else True}
