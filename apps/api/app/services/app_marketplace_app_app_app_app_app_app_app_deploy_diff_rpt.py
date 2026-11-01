"""Deployment diff reporter — compare before/after deployment state."""
from __future__ import annotations


def compare_deployments(before: dict, after: dict) -> dict:
    before_svc = {s["name"]: s for s in before.get("services", [])}
    after_svc = {s["name"]: s for s in after.get("services", [])}
    added = sorted(set(after_svc) - set(before_svc))
    removed = sorted(set(before_svc) - set(after_svc))
    upgraded = []
    downgraded = []
    for name in sorted(set(before_svc) & set(after_svc)):
        bv = before_svc[name].get("version", "")
        av = after_svc[name].get("version", "")
        if bv != av:
            change = {"service": name, "from": bv, "to": av}
            if av > bv:
                upgraded.append(change)
            else:
                downgraded.append(change)
    return {"added": added, "removed": removed, "upgraded": upgraded,
            "downgraded": downgraded,
            "total_changes": len(added) + len(removed) + len(upgraded) + len(downgraded),
            "has_rollbacks": len(downgraded) > 0}
