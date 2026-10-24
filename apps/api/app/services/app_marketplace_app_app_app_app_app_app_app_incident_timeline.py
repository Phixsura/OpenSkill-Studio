"""Incident timeline builder — construct incident timelines from events."""
from __future__ import annotations


def build_timeline(events: list[dict]) -> dict:
    sorted_events = sorted(events, key=lambda e: e["timestamp"])
    phases: dict[str, list[dict]] = {}
    for ev in sorted_events:
        phase = ev.get("phase", "unknown")
        phases.setdefault(phase, []).append(ev)
    first = sorted_events[0]["timestamp"] if sorted_events else None
    last = sorted_events[-1]["timestamp"] if sorted_events else None
    return {"events": sorted_events, "total_events": len(sorted_events),
            "phases": {k: len(v) for k, v in phases.items()},
            "started_at": first, "last_event_at": last}


def calculate_mttr(incidents: list[dict]) -> dict:
    resolved = [i for i in incidents if i.get("resolved_at") and i.get("detected_at")]
    if not resolved:
        return {"mttr_minutes": 0, "resolved_count": 0, "total": len(incidents)}
    ttrs = [(i["resolved_at"] - i["detected_at"]) / 60 for i in resolved]
    avg = round(sum(ttrs) / len(ttrs), 1)
    return {"mttr_minutes": avg, "resolved_count": len(resolved),
            "total": len(incidents), "min_ttr": round(min(ttrs), 1),
            "max_ttr": round(max(ttrs), 1)}
