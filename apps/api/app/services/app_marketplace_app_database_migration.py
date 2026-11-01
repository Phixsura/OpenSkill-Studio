"""Database migration — manage schema migrations for app databases."""

import secrets
from datetime import datetime


def create_migration(*, name: str, up_sql: str, down_sql: str) -> dict:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    migration_id = f"{ts}_{name.lower().replace(' ', '_')}"
    return {
        "migration_id": migration_id,
        "name": name,
        "up_sql": up_sql,
        "down_sql": down_sql,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "checksum": secrets.token_hex(8),
    }


def get_migration_status(*, migrations: list[dict]) -> dict:
    applied = [m for m in migrations if m.get("status") == "applied"]
    pending = [m for m in migrations if m.get("status") == "pending"]
    failed = [m for m in migrations if m.get("status") == "failed"]
    return {
        "total": len(migrations),
        "applied": len(applied),
        "pending": len(pending),
        "failed": len(failed),
        "current_version": applied[-1]["migration_id"] if applied else None,
        "up_to_date": len(pending) == 0 and len(failed) == 0,
    }


def validate_migration(*, up_sql: str, down_sql: str) -> dict:
    errors = []
    dangerous = ["DROP DATABASE", "TRUNCATE", "DROP SCHEMA"]
    for kw in dangerous:
        if kw.lower() in up_sql.lower():
            errors.append(f"Dangerous operation in UP: {kw}")
    if not down_sql.strip():
        errors.append("DOWN migration is empty — rollback not possible")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": []}
