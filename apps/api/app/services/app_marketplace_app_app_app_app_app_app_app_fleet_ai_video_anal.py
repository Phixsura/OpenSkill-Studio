"""Fleet AI Video Analysis — track video understanding and processing."""
from __future__ import annotations
def fleet_ai_video_analysis(analyzers: list[dict]) -> dict:
    active = [a for a in analyzers if a.get("active", True)]
    hours_24h = round(sum(a.get("hours_24h", 0) for a in analyzers), 1)
    fps = round(sum(a.get("fps", 0) for a in analyzers) / max(len(analyzers), 1), 1)
    events_detected = sum(a.get("events", 0) for a in analyzers)
    return {"analyzers": len(analyzers), "active": len(active), "hours_24h": hours_24h,
            "fps": fps, "events": events_detected, "realtime": fps >= 30}
