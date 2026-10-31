"""Bulk actions — batch operations on multiple apps or installations."""

from datetime import datetime, timezone


def bulk_update_status(*, app_ids: list[str], new_status: str, actor_id: str) -> dict:
    valid_statuses = {"draft", "published", "suspended", "archived"}
    if new_status not in valid_statuses:
        return {"error": f"Invalid status: {new_status}", "updated": []}
    results = []
    for app_id in app_ids:
        results.append({"app_id": app_id, "status": new_status, "updated_by": actor_id,
                         "updated_at": datetime.now(timezone.utc).isoformat()})
    return {"updated": results, "count": len(results), "error": None}


def bulk_uninstall(*, installation_ids: list[str], actor_id: str) -> dict:
    results = []
    for inst_id in installation_ids:
        results.append({"installation_id": inst_id, "status": "uninstalled",
                         "uninstalled_by": actor_id})
    return {"uninstalled": results, "count": len(results)}


def validate_bulk_selection(*, ids: list[str], max_batch: int = 50) -> dict:
    if not ids:
        return {"valid": False, "error": "No items selected"}
    if len(ids) > max_batch:
        return {"valid": False, "error": f"Max {max_batch} items per batch"}
    if len(ids) != len(set(ids)):
        return {"valid": False, "error": "Duplicate IDs found"}
    return {"valid": True, "error": None, "count": len(ids)}
