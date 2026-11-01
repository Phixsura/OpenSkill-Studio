"""Fleet SDK adoption — track SDK version distribution."""
from __future__ import annotations
def fleet_sdk_adoption(clients: list[dict]) -> dict:
    by_version: dict[str, int] = {}
    for c in clients:
        v = c.get("sdk_version", "unknown")
        by_version[v] = by_version.get(v, 0) + 1
    outdated = [c for c in clients if c.get("outdated", False)]
    return {"total": len(clients), "versions": by_version, "outdated": len(outdated),
            "up_to_date": len(clients) - len(outdated)}
