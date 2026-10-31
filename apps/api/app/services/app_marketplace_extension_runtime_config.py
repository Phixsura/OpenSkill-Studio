"""Runtime Config — live configuration updates for running extensions.

Supports pushing config changes to running sandboxes without restart,
with rollback, validation, and change notification.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ConfigChange:
    change_id: str
    key: str
    old_value: object
    new_value: object
    applied_at: str = ""
    rolled_back: bool = False

    def __post_init__(self):
        if not self.applied_at:
            self.applied_at = datetime.now(timezone.utc).isoformat()


class RuntimeConfigService:
    """Manages live config updates for running extensions."""

    def __init__(self):
        self._configs: dict[str, dict] = {}  # ext:org -> config
        self._changes: dict[str, list[ConfigChange]] = {}  # ext:org -> history
        self._validators: dict[str, callable] = {}  # key -> validator fn

    def _scope(self, extension_id: str, org_id: str) -> str:
        return f"{extension_id}:{org_id}"

    def set_initial(self, extension_id: str, org_id: str, config: dict) -> None:
        """Set the initial config for a running extension."""
        scope = self._scope(extension_id, org_id)
        self._configs[scope] = deepcopy(config)
        self._changes[scope] = []

    def register_validator(self, key: str, validator: callable) -> None:
        """Register a validator for a config key. validator(value) -> (ok, error)."""
        self._validators[key] = validator

    def update(self, extension_id: str, org_id: str, key: str,
               value: object) -> tuple[bool, str]:
        """Update a single config key at runtime."""
        scope = self._scope(extension_id, org_id)
        config = self._configs.get(scope)
        if config is None:
            return False, "No config for this scope"

        # Validate
        validator = self._validators.get(key)
        if validator:
            ok, err = validator(value)
            if not ok:
                return False, f"Validation failed: {err}"

        old_value = config.get(key)
        config[key] = deepcopy(value)

        change_id = f"chg-{len(self._changes.get(scope, []))+1}"
        self._changes.setdefault(scope, []).append(
            ConfigChange(change_id, key, deepcopy(old_value), deepcopy(value))
        )
        return True, "Updated"

    def batch_update(self, extension_id: str, org_id: str,
                     updates: dict) -> tuple[bool, list[str]]:
        """Update multiple config keys atomically."""
        errors = []
        scope = self._scope(extension_id, org_id)
        config = self._configs.get(scope)
        if config is None:
            return False, ["No config for this scope"]

        # Validate all first
        for key, value in updates.items():
            validator = self._validators.get(key)
            if validator:
                ok, err = validator(value)
                if not ok:
                    errors.append(f"{key}: {err}")
        if errors:
            return False, errors

        # Apply all
        for key, value in updates.items():
            self.update(extension_id, org_id, key, value)
        return True, []

    def rollback_last(self, extension_id: str, org_id: str) -> tuple[bool, str]:
        """Rollback the most recent config change."""
        scope = self._scope(extension_id, org_id)
        changes = self._changes.get(scope, [])
        if not changes:
            return False, "No changes to rollback"
        last = changes[-1]
        if last.rolled_back:
            return False, "Already rolled back"
        config = self._configs.get(scope, {})
        config[last.key] = deepcopy(last.old_value)
        last.rolled_back = True
        return True, f"Rolled back {last.key}"

    def get_config(self, extension_id: str, org_id: str) -> dict:
        scope = self._scope(extension_id, org_id)
        return deepcopy(self._configs.get(scope, {}))

    def get_history(self, extension_id: str, org_id: str) -> list[ConfigChange]:
        scope = self._scope(extension_id, org_id)
        return list(self._changes.get(scope, []))
