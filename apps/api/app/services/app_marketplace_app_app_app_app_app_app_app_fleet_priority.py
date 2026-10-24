"""Fleet priority classes — track pod priority distribution."""
from __future__ import annotations
def fleet_priority_classes(pods: list[dict]) -> dict:
    by_priority: dict[str, int] = {}
    for p in pods:
        pc = p.get("priority_class", "default")
        by_priority[pc] = by_priority.get(pc, 0) + 1
    no_priority = by_priority.get("default", 0)
    return {"total": len(pods), "by_class": by_priority,
            "no_priority": no_priority, "all_prioritized": no_priority == 0}
