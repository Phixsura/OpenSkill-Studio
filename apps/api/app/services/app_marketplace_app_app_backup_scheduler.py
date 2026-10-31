"""Backup scheduler — automated backup configuration and status."""

import secrets
import html
from datetime import datetime, timezone, timedelta


def create_backup_schedule(*, name: str, frequency: str = "daily",
                             retention_days: int = 30, enabled: bool = True) -> dict:
    schedule_id = f"bak_{secrets.token_hex(6)}"
    cron = {"hourly": "0 * * * *", "daily": "0 2 * * *",
            "weekly": "0 2 * * 0", "monthly": "0 2 1 * *"}.get(frequency, "0 2 * * *")
    return {"id": schedule_id, "name": html.escape(name), "frequency": frequency,
            "cron": cron, "retention_days": retention_days, "enabled": enabled,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "next_run": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}


def build_backup_status(*, backups: list[dict]) -> dict:
    items = sorted(backups, key=lambda b: b.get("created_at", ""), reverse=True)
    total_size = sum(b.get("size_mb", 0) for b in items)
    success = sum(1 for b in items if b.get("status") == "completed")
    return {"backups": items[:10], "total": len(items),
            "total_size_mb": round(total_size, 1), "success_count": success,
            "latest": items[0] if items else None}
