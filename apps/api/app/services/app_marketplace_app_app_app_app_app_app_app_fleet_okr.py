"""Fleet OKR tracker — track objectives and key results."""
from __future__ import annotations
def fleet_okr_tracker(okrs: list[dict]) -> dict:
    on_track = [o for o in okrs if o.get("progress_pct", 0) >= 70]
    at_risk = [o for o in okrs if 30 <= o.get("progress_pct", 0) < 70]
    behind = [o for o in okrs if o.get("progress_pct", 0) < 30]
    avg = round(sum(o.get("progress_pct", 0) for o in okrs) / max(len(okrs), 1), 1)
    return {"total": len(okrs), "on_track": len(on_track), "at_risk": len(at_risk),
            "behind": len(behind), "avg_progress": avg}
