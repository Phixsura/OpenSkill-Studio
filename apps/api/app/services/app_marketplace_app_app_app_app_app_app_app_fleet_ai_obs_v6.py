"""Fleet AI Observability v6 — track ultimate observability stack."""
from __future__ import annotations
def fleet_ai_observability_v6(stacks: list[dict]) -> dict:
    active = [s for s in stacks if s.get("active", True)]
    pillars = sum(1 for s in stacks if s.get("metrics") and s.get("traces") and s.get("logs"))
    dashboards = sum(s.get("dashboards", 0) for s in stacks)
    alerts = sum(s.get("alerts", 0) for s in stacks)
    return {"stacks": len(stacks), "active": len(active), "pillars": pillars,
            "dashboards": dashboards, "alerts": alerts, "complete": pillars == len(stacks)}
