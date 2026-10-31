"""Infrastructure drift detector — detect drift between desired and actual state."""
from __future__ import annotations


def detect_infra_drift(desired: dict[str, dict], actual: dict[str, dict]) -> dict:
    drifted = []
    missing = sorted(set(desired) - set(actual))
    extra = sorted(set(actual) - set(desired))
    for resource in sorted(set(desired) & set(actual)):
        changes = {}
        for key in set(desired[resource]) | set(actual[resource]):
            d_val = desired[resource].get(key)
            a_val = actual[resource].get(key)
            if d_val != a_val:
                changes[key] = {"desired": d_val, "actual": a_val}
        if changes:
            drifted.append({"resource": resource, "changes": changes})
    has_drift = bool(drifted or missing or extra)
    return {"has_drift": has_drift, "drifted": drifted, "missing": missing,
            "extra": extra, "total_issues": len(drifted) + len(missing) + len(extra)}
