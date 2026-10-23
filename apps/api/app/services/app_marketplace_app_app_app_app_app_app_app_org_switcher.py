"""Organization switcher — manage multi-org context switching."""
from __future__ import annotations


def build_org_list(orgs: list[dict], *, current_org_id: str) -> dict:
    items = []
    current = None
    for o in orgs:
        item = {"id": o["id"], "name": o.get("name", ""),
                "role": o.get("role", "member"),
                "plan": o.get("plan", "free"),
                "active": o["id"] == current_org_id}
        items.append(item)
        if item["active"]:
            current = item
    return {"orgs": items, "current": current, "total": len(items),
            "can_create": len(items) < 10}


def get_org_context(org: dict) -> dict:
    return {"org_id": org["id"], "name": org.get("name", ""),
            "plan": org.get("plan", "free"),
            "features": _plan_features(org.get("plan", "free"))}


def _plan_features(plan: str) -> list[str]:
    if plan == "enterprise":
        return ["sso", "audit_logs", "custom_domain", "sla", "priority_support"]
    if plan == "pro":
        return ["sso", "audit_logs", "custom_domain"]
    if plan == "starter":
        return ["custom_domain"]
    return []
