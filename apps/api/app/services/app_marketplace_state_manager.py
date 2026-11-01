"""State Manager — persistent state management for sandboxed extensions.

Provides a key-value store with namespacing, TTL, size limits, and
atomic operations for extensions to persist state across executions.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class StateEntry:
    key: str
    value: object
    namespace: str
    created_at: float
    updated_at: float
    ttl: float | None = None  # None = no expiry
    size_bytes: int = 0


class StateManager:
    """Key-value state store for extensions with namespacing and TTL."""

    def __init__(self, max_keys_per_ns: int = 1000, max_value_bytes: int = 65536):
        self._state: dict[str, dict[str, StateEntry]] = {}  # namespace -> key -> entry
        self._max_keys = max_keys_per_ns
        self._max_value = max_value_bytes

    def _ns_key(self, extension_id: str, org_id: str = "") -> str:
        return f"{extension_id}:{org_id}" if org_id else extension_id

    def set(self, extension_id: str, key: str, value: object,
            org_id: str = "", ttl: float | None = None) -> tuple[bool, str]:
        """Set a state value."""
        ns = self._ns_key(extension_id, org_id)
        size = len(str(value))
        if size > self._max_value:
            return False, f"Value too large: {size} > {self._max_value}"

        ns_state = self._state.setdefault(ns, {})
        if key not in ns_state and len(ns_state) >= self._max_keys:
            return False, "Max keys per namespace exceeded"

        now = time.monotonic()
        ns_state[key] = StateEntry(
            key=key, value=deepcopy(value), namespace=ns,
            created_at=now, updated_at=now, ttl=ttl, size_bytes=size,
        )
        return True, "OK"

    def get(self, extension_id: str, key: str, org_id: str = "") -> object | None:
        """Get a state value, respecting TTL."""
        ns = self._ns_key(extension_id, org_id)
        entry = self._state.get(ns, {}).get(key)
        if not entry:
            return None
        if entry.ttl and time.monotonic() - entry.updated_at > entry.ttl:
            self._state[ns].pop(key, None)
            return None
        return deepcopy(entry.value)

    def delete(self, extension_id: str, key: str, org_id: str = "") -> bool:
        ns = self._ns_key(extension_id, org_id)
        return self._state.get(ns, {}).pop(key, None) is not None

    def exists(self, extension_id: str, key: str, org_id: str = "") -> bool:
        return self.get(extension_id, key, org_id) is not None

    def increment(self, extension_id: str, key: str, amount: int = 1,
                  org_id: str = "") -> int | None:
        """Atomic increment of a numeric value."""
        current = self.get(extension_id, key, org_id)
        if current is None:
            self.set(extension_id, key, amount, org_id)
            return amount
        if not isinstance(current, (int, float)):
            return None
        new_val = current + amount
        self.set(extension_id, key, new_val, org_id)
        return new_val

    def list_keys(self, extension_id: str, org_id: str = "") -> list[str]:
        ns = self._ns_key(extension_id, org_id)
        return sorted(self._state.get(ns, {}).keys())

    def clear_namespace(self, extension_id: str, org_id: str = "") -> int:
        ns = self._ns_key(extension_id, org_id)
        count = len(self._state.get(ns, {}))
        self._state.pop(ns, None)
        return count

    def get_namespace_stats(self, extension_id: str, org_id: str = "") -> dict:
        ns = self._ns_key(extension_id, org_id)
        entries = self._state.get(ns, {})
        return {
            "namespace": ns,
            "key_count": len(entries),
            "total_bytes": sum(e.size_bytes for e in entries.values()),
            "max_keys": self._max_keys,
        }
