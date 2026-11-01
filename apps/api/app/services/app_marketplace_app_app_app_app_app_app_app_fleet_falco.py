"""Fleet Falco — track runtime security events."""
from __future__ import annotations
def fleet_falco_status(nodes: list[dict]) -> dict:
    active = [n for n in nodes if n.get("falco_running", True)]
    total_alerts = sum(n.get("alerts_24h", 0) for n in nodes)
    critical = sum(n.get("critical_alerts", 0) for n in nodes)
    return {"nodes": len(nodes), "active": len(active), "alerts_24h": total_alerts,
            "critical": critical, "clean": critical == 0}
