"""Session analytics — track user session metrics."""
from __future__ import annotations


def analyze_sessions(sessions: list[dict]) -> dict:
    total = len(sessions)
    durations = [s.get("duration_sec", 0) for s in sessions]
    pages = [s.get("pages_viewed", 0) for s in sessions]
    bounced = sum(1 for s in sessions if s.get("pages_viewed", 0) <= 1)
    avg_duration = round(sum(durations) / max(total, 1))
    avg_pages = round(sum(pages) / max(total, 1), 1)
    bounce_rate = round(bounced / max(total, 1) * 100, 1)
    by_source: dict[str, int] = {}
    for s in sessions:
        src = s.get("source", "direct")
        by_source[src] = by_source.get(src, 0) + 1
    return {"total_sessions": total, "avg_duration_sec": avg_duration,
            "avg_pages": avg_pages, "bounce_rate": bounce_rate,
            "by_source": by_source, "top_source": max(by_source, key=by_source.get) if by_source else None}
