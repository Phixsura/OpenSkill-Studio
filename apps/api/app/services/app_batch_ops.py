"""Batch operations helper — bulk operations on apps/installations."""


def batch_results(operations: list[dict]) -> dict:
    """Compute batch operation summary."""
    success = sum(1 for o in operations if o.get("status") == "success")
    failed = sum(1 for o in operations if o.get("status") == "failed")
    skipped = sum(1 for o in operations if o.get("status") == "skipped")
    return {
        "total": len(operations),
        "success": success,
        "failed": failed,
        "skipped": skipped,
        "all_success": failed == 0 and skipped == 0,
        "results": operations,
    }


def validate_batch_size(items: list, *, max_batch: int = 100) -> list[str]:
    """Validate batch operation size."""
    errors = []
    if len(items) == 0:
        errors.append("Batch cannot be empty")
    elif len(items) > max_batch:
        errors.append(f"Batch too large ({len(items)} items, max {max_batch})")
    return errors
