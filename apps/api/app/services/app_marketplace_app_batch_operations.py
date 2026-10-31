"""Batch operations — execute bulk actions on multiple resources."""

import secrets
from datetime import datetime


def create_batch(*, operation: str, resource_ids: list[str],
                   params: dict | None = None) -> dict:
    valid_ops = {"update", "delete", "export", "tag", "archive", "restore"}
    if operation not in valid_ops:
        return {"error": f"Invalid operation. Valid: {', '.join(sorted(valid_ops))}"}
    if not resource_ids:
        return {"error": "No resources specified"}
    if len(resource_ids) > 100:
        return {"error": "Max 100 resources per batch"}
    return {
        "batch_id": f"batch_{secrets.token_urlsafe(8)}",
        "operation": operation,
        "resource_count": len(resource_ids),
        "resource_ids": resource_ids,
        "params": params or {},
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }


def get_batch_progress(*, total: int, completed: int, failed: int) -> dict:
    remaining = total - completed - failed
    pct = round(completed / max(total, 1) * 100, 1)
    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "remaining": remaining,
        "progress_pct": pct,
        "status": "completed" if remaining == 0 else "in_progress",
        "success_rate": round(completed / max(completed + failed, 1) * 100, 1),
    }
