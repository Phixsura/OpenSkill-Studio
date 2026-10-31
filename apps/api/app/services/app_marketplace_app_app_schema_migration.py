"""Schema migration — track and apply database schema changes."""

import html
import secrets
from datetime import datetime, timezone


def create_migration(*, name: str, up_sql: str, down_sql: str) -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    migration_id = f"{ts}_{name.replace(' ', '_').lower()}"
    return {"id": migration_id, "name": html.escape(name),
            "up_sql": up_sql, "down_sql": down_sql,
            "status": "pending", "created_at": datetime.now(timezone.utc).isoformat(),
            "checksum": secrets.token_hex(8)}


def build_migration_history(*, migrations: list[dict]) -> dict:
    applied = [m for m in migrations if m.get("status") == "applied"]
    pending = [m for m in migrations if m.get("status") == "pending"]
    failed = [m for m in migrations if m.get("status") == "failed"]
    return {"total": len(migrations), "applied": len(applied),
            "pending": len(pending), "failed": len(failed),
            "latest": applied[-1]["id"] if applied else None,
            "needs_migration": len(pending) > 0,
            "has_failures": len(failed) > 0}
