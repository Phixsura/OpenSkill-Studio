"""Telemetry collector — collect and aggregate app telemetry data."""

from collections import defaultdict
from datetime import datetime, timezone


def collect_telemetry_event(*, app_id: str, event_name: str, properties: dict,
                               session_id: str | None = None) -> dict:
    return {"app_id": app_id, "event_name": event_name, "properties": properties,
            "session_id": session_id, "timestamp": datetime.now(timezone.utc).isoformat()}


def aggregate_telemetry(*, events: list[dict]) -> dict:
    by_event = defaultdict(int)
    by_session = set()
    for e in events:
        by_event[e.get("event_name", "unknown")] += 1
        if e.get("session_id"):
            by_session.add(e["session_id"])
    return {"total_events": len(events), "unique_sessions": len(by_session),
            "event_counts": dict(sorted(by_event.items(), key=lambda x: -x[1]))}


def build_telemetry_funnel(*, events: list[dict], funnel_steps: list[str]) -> dict:
    step_counts = {step: 0 for step in funnel_steps}
    for e in events:
        name = e.get("event_name")
        if name in step_counts:
            step_counts[name] += 1
    steps = []
    for i, step in enumerate(funnel_steps):
        count = step_counts[step]
        prev = step_counts[funnel_steps[i - 1]] if i > 0 else count
        steps.append({"step": step, "count": count,
                       "conversion_pct": round(count / max(prev, 1) * 100, 1)})
    return {"steps": steps, "overall_pct": round(steps[-1]["count"] / max(steps[0]["count"], 1) * 100, 1) if steps else 0}
