"""Network policy analyzer — analyze and audit network policies."""
from __future__ import annotations


def analyze_policies(policies: list[dict]) -> dict:
    allow_count = 0
    deny_count = 0
    by_namespace: dict[str, int] = {}
    overly_permissive = []
    for p in policies:
        if p.get("action") == "allow":
            allow_count += 1
        else:
            deny_count += 1
        ns = p.get("namespace", "default")
        by_namespace[ns] = by_namespace.get(ns, 0) + 1
        if p.get("source") == "*" and p.get("destination") == "*":
            overly_permissive.append(p.get("name", ""))
    return {"total": len(policies), "allow": allow_count, "deny": deny_count,
            "by_namespace": by_namespace, "overly_permissive": overly_permissive,
            "security_score": round(max(0, 100 - len(overly_permissive) * 20))}
