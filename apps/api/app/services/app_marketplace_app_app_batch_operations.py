"""Batch operations — bulk action executor with progress tracking."""

import html
from datetime import datetime, timezone


def execute_batch(*, items: list[str], action: str, dry_run: bool = False) -> dict:
    results = []
    succeeded = failed = skipped = 0
    for item in items:
        if dry_run:
            results.append({"item": html.escape(item), "status": "skipped", "reason": "dry_run"})
            skipped += 1
        elif not item.strip():
            results.append({"item": "", "status": "failed", "reason": "empty_item"})
            failed += 1
        else:
            results.append({"item": html.escape(item), "status": "success", "reason": None})
            succeeded += 1
    return {"action": action, "dry_run": dry_run, "results": results,
            "total": len(items), "succeeded": succeeded, "failed": failed, "skipped": skipped,
            "completed_at": datetime.now(timezone.utc).isoformat()}


def build_batch_summary(*, batches: list[dict]) -> dict:
    total_items = sum(b.get("total", 0) for b in batches)
    total_success = sum(b.get("succeeded", 0) for b in batches)
    return {"batch_count": len(batches), "total_items": total_items,
            "total_success": total_success,
            "success_rate": round(total_success / max(total_items, 1) * 100, 1)}
