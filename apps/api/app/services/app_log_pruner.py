"""Log pruner — prune old logs to control storage."""


def prune_logs(logs: list[dict], *, max_entries: int = 1000, max_age_days: int = 30) -> dict:
    from datetime import UTC, datetime, timedelta
    cutoff = (datetime.now(UTC) - timedelta(days=max_age_days)).isoformat()
    kept = [l for l in logs if l.get("timestamp", "") >= cutoff][-max_entries:]
    pruned = len(logs) - len(kept)
    return {"kept": len(kept), "pruned": pruned, "entries": kept}
