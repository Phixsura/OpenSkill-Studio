"""Tenant isolation — enforce data boundaries between organizations."""


ISOLATION_LEVELS = {
    "shared": {"label": "Shared Infrastructure", "risk": "low", "cost_multiplier": 1.0,
               "features": ["logical_separation", "row_level_security"]},
    "dedicated": {"label": "Dedicated Resources", "risk": "minimal", "cost_multiplier": 2.5,
                  "features": ["separate_compute", "separate_storage", "encryption_at_rest"]},
    "isolated": {"label": "Fully Isolated", "risk": "none", "cost_multiplier": 5.0,
                 "features": ["separate_vpc", "dedicated_keys", "audit_logging", "compliance_cert"]},
}


def get_isolation_config(*, org_id: str, level: str = "shared") -> dict:
    config = ISOLATION_LEVELS.get(level)
    if not config:
        return {"error": f"Invalid level. Valid: {', '.join(ISOLATION_LEVELS)}"}
    return {
        "org_id": org_id,
        "level": level,
        **config,
        "data_residency": "us-east-1",
        "encryption": level != "shared",
        "cross_tenant_blocked": level in ("dedicated", "isolated"),
    }


def verify_tenant_access(*, requesting_org: str, target_org: str,
                           resource_type: str) -> dict:
    if requesting_org == target_org:
        return {"allowed": True, "reason": "Same organization"}
    shared_resources = {"public_apps", "marketplace_listings", "documentation"}
    if resource_type in shared_resources:
        return {"allowed": True, "reason": f"{resource_type} is a shared resource"}
    return {"allowed": False, "reason": "Cross-tenant access denied",
            "requesting_org": requesting_org, "target_org": target_org}
