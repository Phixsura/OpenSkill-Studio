"""Marketplace featured apps — curate featured app lists."""

from datetime import UTC, datetime

_featured: list[dict] = []


def set_featured(apps: list[dict]) -> int:
    """Set the featured apps list."""
    global _featured
    _featured = [{"app_id": a.get("app_id", a.get("id")), "reason": a.get("reason", ""),
                   "position": i, "featured_at": datetime.now(UTC).isoformat()}
                  for i, a in enumerate(apps)]
    return len(_featured)


def get_featured(*, limit: int = 6) -> list[dict]:
    return _featured[:limit]


def add_featured(app_id: str, reason: str = "") -> dict:
    entry = {"app_id": app_id, "reason": reason, "position": len(_featured),
             "featured_at": datetime.now(UTC).isoformat()}
    _featured.append(entry)
    return entry


def remove_featured(app_id: str) -> bool:
    global _featured
    before = len(_featured)
    _featured = [f for f in _featured if f["app_id"] != app_id]
    return len(_featured) < before
