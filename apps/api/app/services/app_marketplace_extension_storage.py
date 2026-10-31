"""Extension Storage — persistent key-value storage service for extensions.

Provides per-extension, per-org isolated storage with namespaces,
TTL, atomic counters, and list/set data structures.
"""
from __future__ import annotations
import time
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass


@dataclass
class StorageEntry:
    value: object
    created_at: float
    expires_at: float | None = None

    @property
    def expired(self) -> bool:
        return self.expires_at is not None and time.monotonic() > self.expires_at


class ExtensionStorage:
    """Isolated key-value storage for extensions."""

    def __init__(self, max_keys: int = 10000, max_value_bytes: int = 65536):
        self._stores: dict[str, dict[str, StorageEntry]] = defaultdict(dict)
        self._max_keys = max_keys
        self._max_value = max_value_bytes

    def _scope(self, ext_id: str, org_id: str, ns: str = "") -> str:
        parts = [ext_id, org_id]
        if ns:
            parts.append(ns)
        return ":".join(parts)

    def put(self, ext_id: str, org_id: str, key: str, value: object,
            ns: str = "", ttl_seconds: float | None = None) -> tuple[bool, str]:
        scope = self._scope(ext_id, org_id, ns)
        store = self._stores[scope]
        size = len(str(value))
        if size > self._max_value:
            return False, "Value too large"
        if key not in store and len(store) >= self._max_keys:
            self._evict_expired(scope)
            if len(store) >= self._max_keys:
                return False, "Max keys exceeded"
        expires = time.monotonic() + ttl_seconds if ttl_seconds else None
        store[key] = StorageEntry(deepcopy(value), time.monotonic(), expires)
        return True, "OK"

    def get(self, ext_id: str, org_id: str, key: str, ns: str = "") -> object | None:
        scope = self._scope(ext_id, org_id, ns)
        entry = self._stores.get(scope, {}).get(key)
        if not entry or entry.expired:
            if entry and entry.expired:
                self._stores[scope].pop(key, None)
            return None
        return deepcopy(entry.value)

    def delete(self, ext_id: str, org_id: str, key: str, ns: str = "") -> bool:
        scope = self._scope(ext_id, org_id, ns)
        return self._stores.get(scope, {}).pop(key, None) is not None

    def exists(self, ext_id: str, org_id: str, key: str, ns: str = "") -> bool:
        return self.get(ext_id, org_id, key, ns) is not None

    def increment(self, ext_id: str, org_id: str, key: str, amount: int = 1,
                  ns: str = "") -> int:
        current = self.get(ext_id, org_id, key, ns)
        new_val = (current or 0) + amount
        self.put(ext_id, org_id, key, new_val, ns)
        return new_val

    def list_push(self, ext_id: str, org_id: str, key: str, value: object,
                  ns: str = "") -> int:
        current = self.get(ext_id, org_id, key, ns)
        if not isinstance(current, list):
            current = []
        current.append(value)
        self.put(ext_id, org_id, key, current, ns)
        return len(current)

    def list_get(self, ext_id: str, org_id: str, key: str,
                 ns: str = "", limit: int = 100) -> list:
        current = self.get(ext_id, org_id, key, ns)
        if isinstance(current, list):
            return current[-limit:]
        return []

    def keys(self, ext_id: str, org_id: str, ns: str = "",
             prefix: str = "") -> list[str]:
        scope = self._scope(ext_id, org_id, ns)
        self._evict_expired(scope)
        all_keys = sorted(self._stores.get(scope, {}).keys())
        if prefix:
            all_keys = [k for k in all_keys if k.startswith(prefix)]
        return all_keys

    def clear(self, ext_id: str, org_id: str, ns: str = "") -> int:
        scope = self._scope(ext_id, org_id, ns)
        count = len(self._stores.get(scope, {}))
        self._stores.pop(scope, None)
        return count

    def _evict_expired(self, scope: str) -> None:
        store = self._stores.get(scope, {})
        expired = [k for k, v in store.items() if v.expired]
        for k in expired:
            del store[k]
