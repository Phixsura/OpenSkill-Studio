"""Tenant isolation checker — verify data isolation between tenants."""
from __future__ import annotations


def check_isolation(resources: list[dict]) -> dict:
    violations = []
    by_tenant: dict[str, list[str]] = {}
    for r in resources:
        tenant = r.get("tenant_id", "")
        rid = r.get("resource_id", "")
        accessible_by = r.get("accessible_by", [tenant])
        by_tenant.setdefault(tenant, []).append(rid)
        for accessor in accessible_by:
            if accessor != tenant and accessor != "system":
                violations.append({
                    "resource": rid, "owner": tenant,
                    "accessed_by": accessor, "severity": "high",
                })
    return {
        "total_resources": len(resources),
        "tenants": len(by_tenant),
        "violations": violations,
        "violation_count": len(violations),
        "isolated": len(violations) == 0,
        "status": "secure" if not violations else "breached",
    }


def generate_isolation_report(check_result: dict) -> dict:
    return {
        "status": check_result["status"],
        "summary": f"{check_result['total_resources']} resources across {check_result['tenants']} tenants",
        "verdict": "✅ All data properly isolated" if check_result["isolated"]
                    else f"❌ {check_result['violation_count']} isolation violations found",
        "violations": check_result["violations"],
    }
