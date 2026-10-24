"""Fleet AI Retention v7 — track AI platform user retention."""
from __future__ import annotations
def fleet_ai_retention_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    d1 = round(sum(t.get("d1_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    d7 = round(sum(t.get("d7_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    d30 = round(sum(t.get("d30_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    d90 = round(sum(t.get("d90_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "d1": d1, "d7": d7,
            "d30": d30, "d90": d90, "sticky": d30 > 50}
