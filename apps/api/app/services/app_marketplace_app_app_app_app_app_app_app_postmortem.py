"""Post-mortem builder — structured outage analysis with blameless retrospective."""
from __future__ import annotations
import html


def build_postmortem(*, title: str, severity: str, duration_min: int,
                      impact: str, root_cause: str, timeline: list[dict],
                      action_items: list[dict], authors: list[str]) -> dict:
    safe_title = html.escape(title)
    mttr_display = f"{duration_min}m" if duration_min < 60 else f"{duration_min // 60}h {duration_min % 60}m"
    tl = [{"time": html.escape(e.get("time", "")),
           "action": html.escape(e.get("action", "")),
           "by": html.escape(e.get("by", ""))} for e in timeline]
    items = [{"task": html.escape(a.get("task", "")),
              "owner": html.escape(a.get("owner", "")),
              "priority": a.get("priority", "medium"),
              "due": a.get("due", "")} for a in action_items]
    p1 = sum(1 for a in items if a["priority"] == "high")
    return {
        "title": safe_title, "severity": severity,
        "duration_min": duration_min, "mttr_display": mttr_display,
        "impact": html.escape(impact), "root_cause": html.escape(root_cause),
        "timeline": tl, "action_items": items,
        "authors": authors, "total_actions": len(items),
        "high_priority_actions": p1,
    }
