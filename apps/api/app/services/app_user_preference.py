"""App User Preference — per-user preference storage for installed apps.

Stores user preferences with typed defaults:
- Get/set preferences per user
- Schema-based defaults
- Bulk get/set operations
- Per-installation scoped preferences
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class PreferenceSchema:
    """Schema defining available preferences with defaults."""

    key: str
    default_value: object
    description: str = ""


class AppUserPreference:
    """Per-user preference storage for installed apps."""

    def __init__(self) -> None:
        # (installation_id) → list[PreferenceSchema]
        self._schemas: dict[str, list[PreferenceSchema]] = {}
        # (installation_id, user_id, key) → value
        self._values: dict[tuple[str, str, str], object] = {}

    def define_schema(
        self,
        installation_id: str,
        preferences: list[PreferenceSchema],
    ) -> None:
        """Define available preferences with defaults."""
        if not installation_id:
            raise ValueError("installation_id is required")
        self._schemas[installation_id] = list(preferences)

    def set_preference(
        self, installation_id: str, user_id: str, key: str, value: object
    ) -> None:
        """Set a user preference."""
        if not user_id:
            raise ValueError("user_id is required")
        if not key:
            raise ValueError("key is required")
        # Validate key exists in schema if schema defined
        schema = self._schemas.get(installation_id, [])
        if schema and not any(s.key == key for s in schema):
            raise ValueError(f"Unknown preference key: {key}")
        self._values[(installation_id, user_id, key)] = value

    def get_preference(
        self, installation_id: str, user_id: str, key: str
    ) -> object:
        """Get a user preference, falling back to schema default."""
        val = self._values.get((installation_id, user_id, key))
        if val is not None:
            return val
        # Check schema default
        for s in self._schemas.get(installation_id, []):
            if s.key == key:
                return s.default_value
        return None

    def get_all(self, installation_id: str, user_id: str) -> dict[str, object]:
        """Get all preferences for a user (with defaults filled in)."""
        result: dict[str, object] = {}
        # Start with schema defaults
        for s in self._schemas.get(installation_id, []):
            result[s.key] = s.default_value
        # Override with user values
        for (inst, uid, key), val in self._values.items():
            if inst == installation_id and uid == user_id:
                result[key] = val
        return result

    def set_bulk(
        self, installation_id: str, user_id: str, preferences: dict[str, object]
    ) -> int:
        """Set multiple preferences at once. Returns count set."""
        count = 0
        for key, value in preferences.items():
            self.set_preference(installation_id, user_id, key, value)
            count += 1
        return count

    def reset_preference(
        self, installation_id: str, user_id: str, key: str
    ) -> None:
        """Reset a preference to its default."""
        self._values.pop((installation_id, user_id, key), None)

    def reset_all(self, installation_id: str, user_id: str) -> int:
        """Reset all preferences for a user. Returns count reset."""
        to_delete = [
            k for k in self._values
            if k[0] == installation_id and k[1] == user_id
        ]
        for k in to_delete:
            del self._values[k]
        return len(to_delete)
