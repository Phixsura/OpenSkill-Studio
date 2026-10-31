"""Fleet Runtime Protection v9 — track RASP and runtime threat detection."""
from __future__ import annotations
def fleet_runtime_protection_v9(agents: list[dict]) -> dict:
    active = [a for a in agents if a.get("active")]
    threats_blocked = sum(a.get("threats_blocked", 0) for a in agents)
    processes_monitored = sum(a.get("processes", 0) for a in agents)
    return {"agents": len(agents), "active": len(active), "threats_blocked": threats_blocked,
            "processes_monitored": processes_monitored, "healthy": len(active) == len(agents)}
