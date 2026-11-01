"""Fleet namespace count — track namespace proliferation."""
from __future__ import annotations
def fleet_namespace_count(namespaces: list[dict]) -> dict:
    active = [n for n in namespaces if n.get("pod_count", 0) > 0]
    empty = [n for n in namespaces if n.get("pod_count", 0) == 0]
    return {"total": len(namespaces), "active": len(active),
            "empty": len(empty), "needs_cleanup": len(empty) > 5}
