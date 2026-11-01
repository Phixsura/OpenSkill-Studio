"""Fleet AI Developer Experience v7 — track ultimate DX metrics."""
from __future__ import annotations
def fleet_ai_dx_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    nps = round(sum(t.get("nps", 0) for t in trackers) / max(len(trackers), 1))
    ttfc = round(sum(t.get("ttfc_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    docs_score = round(sum(t.get("docs_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    sdk_adoption = round(sum(t.get("sdk_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "nps": nps,
            "ttfc_min": ttfc, "docs_pct": docs_score, "sdk_pct": sdk_adoption, "excellent": nps > 60}
