"""Digest builder — email/notification digest aggregation."""

import html
from datetime import datetime, timezone
from collections import defaultdict


def build_digest(*, events: list[dict], period: str = "daily") -> dict:
    by_type: dict[str, list] = defaultdict(list)
    for e in events:
        t = e.get("type", "other")
        by_type[t].append({
            "title": html.escape(e.get("title", "")),
            "description": html.escape(e.get("description", "")),
            "timestamp": e.get("timestamp", ""),
        })
    sections = [{"type": t, "count": len(items), "items": items[:5],
                  "has_more": len(items) > 5}
                 for t, items in sorted(by_type.items())]
    return {"period": period, "sections": sections, "total_events": len(events),
            "section_count": len(sections),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "subject": f"Your {period} digest — {len(events)} updates"}
