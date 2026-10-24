"""Manifest history — track manifest changes across versions."""

from datetime import UTC, datetime
from app.services.app_manifest_differ import diff_fields


def build_history_entry(*, version: str, manifest: dict, previous_manifest: dict | None = None) -> dict:
    changes = diff_fields(previous_manifest or {}, manifest) if previous_manifest else []
    return {
        "version": version,
        "timestamp": datetime.now(UTC).isoformat(),
        "changes": changes,
        "change_count": len(changes),
        "is_initial": previous_manifest is None,
    }


def build_full_history(versions: list[dict]) -> list[dict]:
    """Build history from ordered list of {version, manifest}."""
    history = []
    for i, v in enumerate(versions):
        prev = versions[i - 1]["manifest"] if i > 0 else None
        history.append(build_history_entry(version=v["version"], manifest=v["manifest"], previous_manifest=prev))
    return history
