"""Fleet AI Developer Experience — track DX metrics and satisfaction."""
from __future__ import annotations
def fleet_ai_developer_experience(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    nps = round(sum(t.get("nps", 0) for t in trackers) / max(len(trackers), 1))
    time_to_first_call = round(sum(t.get("ttfc_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    docs_helpfulness = round(sum(t.get("docs_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "nps": nps,
            "ttfc_min": time_to_first_call, "docs_pct": docs_helpfulness, "excellent": nps > 50}
