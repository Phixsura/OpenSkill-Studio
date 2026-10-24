"""Infrastructure drift detector — detect config drift in infrastructure."""
from __future__ import annotations


def detect_drift(desired: dict, actual: dict) -> dict:
    drifts = []
    for key in set(desired) | set(actual):
        d_val = desired.get(key)
        a_val = actual.get(key)
        if d_val != a_val:
            drifts.append({"key": key, "desired": d_val, "actual": a_val,
                            "type": "missing" if a_val is None else "extra" if d_val is None else "changed"})
    return {"drifts": drifts, "drift_count": len(drifts),
            "has_drift": len(drifts) > 0, "keys_checked": len(set(desired) | set(actual))}


def drift_summary(resources: list[dict]) -> dict:
    total_drifts = sum(r.get("drift_count", 0) for r in resources)
    drifted = sum(1 for r in resources if r.get("has_drift"))
    return {"total_resources": len(resources), "drifted": drifted,
            "clean": len(resources) - drifted, "total_drifts": total_drifts,
            "drift_pct": round(drifted / max(len(resources), 1) * 100)}
