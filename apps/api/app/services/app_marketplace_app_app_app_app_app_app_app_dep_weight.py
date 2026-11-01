"""Service dependency weight — calculate dependency criticality weights."""
from __future__ import annotations

def calculate_weights(services: list[dict]) -> dict:
    weights = {}
    for svc in services:
        deps = svc.get("depends_on", [])
        w = len(deps) * 10 + svc.get("request_volume", 0) / 1000
        weights[svc["name"]] = round(w, 1)
    ranked = sorted(weights.items(), key=lambda x: -x[1])
    return {"weights": dict(ranked), "most_critical": ranked[0][0] if ranked else None}
