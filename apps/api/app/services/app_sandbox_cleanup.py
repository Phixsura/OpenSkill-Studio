"""Sandbox cleanup — clean up stale executions and temporary files."""

from datetime import UTC, datetime, timedelta
from collections import defaultdict

_stale_executions: list[dict] = []


def find_stale_executions(executions: list[dict], *, max_age_hours: int = 24) -> list[dict]:
    """Find executions older than max_age_hours that are still running."""
    cutoff = datetime.now(UTC) - timedelta(hours=max_age_hours)
    stale = []
    for ex in executions:
        if ex.get("status") in ("running", "pending"):
            created = datetime.fromisoformat(ex.get("created_at", "").replace("Z", "+00:00"))
            if created < cutoff:
                stale.append(ex)
    return stale


def compute_cleanup_plan(stale: list[dict]) -> dict:
    """Compute what to clean up."""
    by_app: dict[str, int] = defaultdict(int)
    for ex in stale:
        by_app[ex.get("app_id", "unknown")] += 1
    return {
        "total_stale": len(stale),
        "by_app": dict(by_app),
        "action": "cancel_and_cleanup",
        "estimated_freed_mb": len(stale) * 50,  # rough estimate
    }
