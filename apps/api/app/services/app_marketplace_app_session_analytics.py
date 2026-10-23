"""Session analytics — track user sessions within installed apps."""

from collections import defaultdict


def compute_session_metrics(*, sessions: list[dict]) -> dict:
    if not sessions:
        return {"total": 0, "avg_duration_s": 0, "bounce_rate": 0}
    total = len(sessions)
    durations = [s.get("duration_s", 0) for s in sessions]
    bounces = sum(1 for s in sessions if s.get("page_views", 0) <= 1)
    return {
        "total": total, "avg_duration_s": round(sum(durations) / total),
        "median_duration_s": sorted(durations)[total // 2],
        "bounce_rate": round(bounces / total * 100, 1),
        "avg_page_views": round(sum(s.get("page_views", 0) for s in sessions) / total, 1),
    }


def group_sessions_by_source(*, sessions: list[dict]) -> list[dict]:
    by_source = defaultdict(int)
    for s in sessions:
        by_source[s.get("source", "direct")] += 1
    return [{"source": src, "count": cnt, "pct": round(cnt / max(len(sessions), 1) * 100, 1)}
            for src, cnt in sorted(by_source.items(), key=lambda x: -x[1])]
