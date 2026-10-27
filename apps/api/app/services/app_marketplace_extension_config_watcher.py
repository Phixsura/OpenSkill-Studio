"""Config Watcher — detect config changes and trigger reload with validation.

Implements:
- Watch config values for changes
- Change diff reporting
- Validate new config before applying
- Rollback on validation failure
- Change listeners (callbacks on specific keys)
- Change history with timestamps
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from copy import deepcopy


@dataclass
class ConfigChange:
    key: str
    old_value: object
    new_value: object
    timestamp: float = 0.0
    applied: bool = False
    rolled_back: bool = False


class ConfigWatcherService:
    def __init__(self):
        self._config: dict = {}
        self._previous: dict = {}
        self._listeners: dict[str, list[callable]] = {}  # key → callbacks
        self._validators: dict[str, callable] = {}  # key → validator(value) → bool
        self._history: list[ConfigChange] = []

    def load(self, config: dict) -> None:
        """Load initial config."""
        self._config = deepcopy(config)
        self._previous = deepcopy(config)

    def get(self, key: str, default: object = None) -> object:
        return self._config.get(key, default)

    def get_all(self) -> dict:
        return deepcopy(self._config)

    def update(self, changes: dict) -> dict:
        """Apply config changes. Validates, notifies listeners, tracks history.
        Returns {applied: [...], rejected: [...], rolled_back: [...]}."""
        result = {"applied": [], "rejected": [], "rolled_back": []}

        for key, new_value in changes.items():
            old_value = self._config.get(key)
            if old_value == new_value:
                continue  # no change

            # Validate
            validator = self._validators.get(key)
            if validator:
                try:
                    if not validator(new_value):
                        result["rejected"].append({"key": key, "reason": "validation failed"})
                        continue
                except Exception as e:
                    result["rejected"].append({"key": key, "reason": str(e)})
                    continue

            # Apply
            change = ConfigChange(key=key, old_value=old_value,
                                  new_value=new_value, timestamp=time.time(),
                                  applied=True)
            self._previous[key] = old_value
            self._config[key] = new_value
            self._history.append(change)
            result["applied"].append(key)

            # Notify listeners
            for listener in self._listeners.get(key, []):
                try:
                    listener(key, old_value, new_value)
                except Exception:
                    pass

            # Also notify wildcard listeners
            for listener in self._listeners.get("*", []):
                try:
                    listener(key, old_value, new_value)
                except Exception:
                    pass

        return result

    def rollback(self, key: str) -> bool:
        """Rollback a key to its previous value."""
        if key not in self._previous:
            return False
        old = self._previous[key]
        current = self._config.get(key)
        self._config[key] = old
        self._history.append(ConfigChange(
            key=key, old_value=current, new_value=old,
            timestamp=time.time(), applied=True, rolled_back=True))
        return True

    def on_change(self, key: str, callback: callable) -> None:
        """Register a listener for a specific key (or "*" for all)."""
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(callback)

    def add_validator(self, key: str, validator: callable) -> None:
        """Add validation for a key. validator(value) → bool."""
        self._validators[key] = validator

    def diff(self, new_config: dict) -> list[dict]:
        """Compute diff between current and proposed config."""
        changes = []
        all_keys = set(self._config) | set(new_config)
        for key in sorted(all_keys):
            old = self._config.get(key)
            new = new_config.get(key)
            if old != new:
                changes.append({"key": key, "old": old, "new": new,
                                "type": "added" if old is None else
                                        "removed" if new is None else "changed"})
        return changes

    def get_history(self, key: str = "", limit: int = 50) -> list[dict]:
        history = self._history
        if key:
            history = [h for h in history if h.key == key]
        return [{"key": h.key, "old": h.old_value, "new": h.new_value,
                 "timestamp": h.timestamp, "rolled_back": h.rolled_back}
                for h in history[-limit:]]
