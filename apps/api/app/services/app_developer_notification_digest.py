"""Notification digest — build daily/weekly digest of developer events."""

from collections import defaultdict


def build_digest(events: list[dict], *, period: str = "daily") -> dict:
    by_type = defaultdict(list)
    for e in events:
        by_type[e.get("type", "other")].append(e)
    
    highlights = []
    if by_type.get("app_installed"):
        highlights.append(f"📥 {len(by_type['app_installed'])} new installs")
    if by_type.get("review_decided"):
        highlights.append(f"📝 {len(by_type['review_decided'])} reviews completed")
    if by_type.get("error"):
        highlights.append(f"❌ {len(by_type['error'])} errors")
    
    return {"period": period, "total_events": len(events), "highlights": highlights,
            "by_type": {k: len(v) for k, v in by_type.items()}}
