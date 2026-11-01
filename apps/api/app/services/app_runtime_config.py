"""App Runtime Config — hot-reload configuration without restarts.

Manages runtime configuration that can change without deployment:
- Set/get config values with versioning
- Track config change history
- Rollback to previous versions
- Per-installation scoped config
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ConfigVersion:
    """A versioned config snapshot."""

    version: int
    values: dict
    changed_by: str
    timestamp: float


class AppRuntimeConfig:
    """Hot-reload configuration without restarts."""

    def __init__(self) -> None:
        # installation_id → current values
        self._current: dict[str, dict] = {}
        # installation_id → list[ConfigVersion]
        self._history: dict[str, list[ConfigVersion]] = {}

    def set_values(
        self,
        installation_id: str,
        values: dict,
        changed_by: str = "system",
        now: float | None = None,
    ) -> ConfigVersion:
        """Set config values, creating a new version."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not values:
            raise ValueError("values cannot be empty")

        now = now or time.time()
        history = self._history.setdefault(installation_id, [])
        current = dict(self._current.get(installation_id, {}))
        current.update(values)
        self._current[installation_id] = current

        version = ConfigVersion(
            version=len(history) + 1,
            values=dict(current),
            changed_by=changed_by,
            timestamp=now,
        )
        history.append(version)
        return version

    def get_value(self, installation_id: str, key: str, default: object = None) -> object:
        return self._current.get(installation_id, {}).get(key, default)

    def get_all(self, installation_id: str) -> dict:
        return dict(self._current.get(installation_id, {}))

    def get_version(self, installation_id: str) -> int:
        history = self._history.get(installation_id, [])
        return len(history)

    def get_history(self, installation_id: str, limit: int = 10) -> list[ConfigVersion]:
        history = self._history.get(installation_id, [])
        return list(reversed(history[-limit:]))

    def rollback(self, installation_id: str, to_version: int) -> ConfigVersion:
        """Rollback to a previous config version."""
        history = self._history.get(installation_id, [])
        if to_version < 1 or to_version > len(history):
            raise ValueError(f"Invalid version {to_version}")

        target = history[to_version - 1]
        self._current[installation_id] = dict(target.values)

        rollback_ver = ConfigVersion(
            version=len(history) + 1,
            values=dict(target.values),
            changed_by=f"rollback_to_v{to_version}",
            timestamp=time.time(),
        )
        history.append(rollback_ver)
        return rollback_ver

    def delete_key(self, installation_id: str, key: str) -> bool:
        current = self._current.get(installation_id, {})
        if key in current:
            del current[key]
            return True
        return False
