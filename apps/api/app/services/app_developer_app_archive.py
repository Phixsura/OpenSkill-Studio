"""App archive — manage archived (soft-deleted) apps."""

from datetime import UTC, datetime

_archive: dict[str, dict] = {}


def archive_app(*, app_id: str, app_data: dict, reason: str = "") -> dict:
    entry = {**app_data, "archived_at": datetime.now(UTC).isoformat(), "archive_reason": reason}
    _archive[app_id] = entry
    return entry


def restore_app(app_id: str) -> dict | None:
    return _archive.pop(app_id, None)


def get_archived(developer_id: str) -> list[dict]:
    return [a for a in _archive.values() if a.get("developer_id") == developer_id]


def is_archived(app_id: str) -> bool:
    return app_id in _archive
