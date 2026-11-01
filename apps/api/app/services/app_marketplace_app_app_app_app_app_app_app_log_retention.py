"""Log retention policy — manage log retention and cleanup policies."""
from __future__ import annotations


def evaluate_retention(logs: list[dict], policies: dict[str, int]) -> dict:
    to_keep = []
    to_delete = []
    for log in logs:
        log_type = log.get("type", "general")
        retention_days = policies.get(log_type, policies.get("default", 30))
        age_days = log.get("age_days", 0)
        if age_days > retention_days:
            to_delete.append(log)
        else:
            to_keep.append(log)
    size_freed = sum(l.get("size_mb", 0) for l in to_delete)
    return {"to_keep": len(to_keep), "to_delete": len(to_delete),
            "size_freed_mb": round(size_freed, 1), "total": len(logs)}


def storage_projection(current_size_gb: float, daily_ingest_gb: float,
                        retention_days: int) -> dict:
    max_storage = round(daily_ingest_gb * retention_days, 1)
    pct_of_max = round(current_size_gb / max(max_storage, 0.01) * 100, 1)
    return {"current_gb": current_size_gb, "max_projected_gb": max_storage,
            "daily_ingest_gb": daily_ingest_gb, "retention_days": retention_days,
            "pct_of_max": pct_of_max}
