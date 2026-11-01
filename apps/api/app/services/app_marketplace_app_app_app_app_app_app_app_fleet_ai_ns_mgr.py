"""Fleet AI Namespace Manager — track AI resource namespace isolation."""
from __future__ import annotations
def fleet_ai_namespace_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    namespaces = sum(m.get("namespaces", 0) for m in managers)
    resources = sum(m.get("resources", 0) for m in managers)
    conflicts = sum(m.get("conflicts", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "namespaces": namespaces,
            "resources": resources, "conflicts": conflicts, "clean": conflicts == 0}
