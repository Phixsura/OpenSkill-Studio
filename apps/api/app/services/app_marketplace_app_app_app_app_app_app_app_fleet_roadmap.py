"""Fleet roadmap progress — track feature roadmap delivery."""
from __future__ import annotations
def fleet_roadmap_progress(items: list[dict]) -> dict:
    done = [i for i in items if i.get("status") == "done"]
    in_progress = [i for i in items if i.get("status") == "in_progress"]
    planned = [i for i in items if i.get("status") == "planned"]
    pct = round(len(done) / max(len(items), 1) * 100, 1)
    return {"total": len(items), "done": len(done), "in_progress": len(in_progress),
            "planned": len(planned), "completion_pct": pct}
