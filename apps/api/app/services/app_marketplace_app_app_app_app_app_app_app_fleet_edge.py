"""Fleet edge computing — track edge node health."""
from __future__ import annotations
def fleet_edge_computing(nodes: list[dict]) -> dict:
    online = [n for n in nodes if n.get("status") == "online"]
    offline = [n for n in nodes if n.get("status") == "offline"]
    total_rps = sum(n.get("rps", 0) for n in online)
    return {"total": len(nodes), "online": len(online), "offline": len(offline),
            "total_rps": total_rps, "all_online": len(offline) == 0}
