"""404 handler — comprehensive not-found handler with analytics."""

import html
from collections import defaultdict
from datetime import datetime, timezone


def log_404(*, path: str, referrer: str = "", user_agent: str = "") -> dict:
    return {"path": html.escape(path), "referrer": html.escape(referrer[:200]),
            "user_agent": html.escape(user_agent[:100]),
            "timestamp": datetime.now(timezone.utc).isoformat()}


def analyze_404s(*, logs: list[dict]) -> dict:
    path_counts: dict[str, int] = defaultdict(int)
    referrer_counts: dict[str, int] = defaultdict(int)
    for log in logs:
        path_counts[log.get("path", "")] += 1
        ref = log.get("referrer", "")
        if ref:
            referrer_counts[ref] += 1
    top_paths = sorted(path_counts.items(), key=lambda x: -x[1])[:10]
    top_referrers = sorted(referrer_counts.items(), key=lambda x: -x[1])[:5]
    return {"total": len(logs),
            "unique_paths": len(path_counts),
            "top_paths": [{"path": p, "count": c} for p, c in top_paths],
            "top_referrers": [{"referrer": r, "count": c} for r, c in top_referrers],
            "needs_attention": any(c >= 10 for _, c in top_paths)}
