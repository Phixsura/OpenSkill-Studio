"""Batch operations — execute operations across multiple installations."""

from datetime import datetime, timezone


def create_batch_job(*, operation: str, target_ids: list[str], params: dict | None = None) -> dict:
    valid_ops = {"update_config", "restart", "enable_flag", "disable_flag", "rotate_secrets"}
    if operation not in valid_ops:
        return {"error": f"Invalid operation. Use: {', '.join(sorted(valid_ops))}"}
    if not target_ids:
        return {"error": "No targets specified"}
    return {
        "operation": operation, "targets": target_ids, "params": params or {},
        "total": len(target_ids), "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(), "error": None,
    }


def execute_batch(*, job: dict) -> dict:
    results = []
    for target_id in job["targets"]:
        results.append({"target_id": target_id, "status": "success"})
    succeeded = sum(1 for r in results if r["status"] == "success")
    return {"results": results, "succeeded": succeeded, "failed": len(results) - succeeded,
            "completed_at": datetime.now(timezone.utc).isoformat()}


def get_batch_progress(*, total: int, completed: int) -> dict:
    return {"total": total, "completed": completed, "remaining": total - completed,
            "pct": round(completed / max(total, 1) * 100)}
