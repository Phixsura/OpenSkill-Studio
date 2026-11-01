"""Tenant isolation validator — verify data isolation between tenants."""
from __future__ import annotations


def validate_isolation(resources: list[dict]) -> dict:
    violations = []
    tenant_resources: dict[str, set] = {}
    for r in resources:
        tid = r["tenant_id"]
        rid = r["resource_id"]
        tenant_resources.setdefault(tid, set()).add(rid)
    # Check for cross-tenant resource sharing
    all_rids: dict[str, list[str]] = {}
    for tid, rids in tenant_resources.items():
        for rid in rids:
            all_rids.setdefault(rid, []).append(tid)
    for rid, tenants in all_rids.items():
        if len(tenants) > 1:
            violations.append({"resource_id": rid, "tenants": sorted(tenants),
                               "severity": "critical"})
    return {"valid": len(violations) == 0, "violations": violations,
            "tenants_checked": len(tenant_resources),
            "resources_checked": len(all_rids)}


def check_namespace(tenant_id: str, namespace: str) -> dict:
    expected_prefix = f"t-{tenant_id}-"
    valid = namespace.startswith(expected_prefix)
    return {"tenant_id": tenant_id, "namespace": namespace,
            "valid": valid, "expected_prefix": expected_prefix}
