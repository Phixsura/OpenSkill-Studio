"""Sandbox KV Store — key-value storage for extension sandboxes.

Provides a simple key-value store with TTL, namespaces, size limits,
atomic operations (increment, append), and prefix scanning.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class KVEntry:
    key: str
    value: str
    ttl: float = 0  # 0 = no expiry
    created_at: float = 0.0
    size_bytes: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        self.size_bytes = len(self.value.encode())

    @property
    def is_expired(self) -> bool:
        return self.ttl != 0 and time.time() - self.created_at > self.ttl


class SandboxKVStoreService:
    """Key-value store for extension sandboxes with TTL and namespaces."""

    MAX_KEY_LENGTH = 256
    MAX_VALUE_SIZE = 1024 * 1024  # 1MB
    MAX_ENTRIES = 10000

    def __init__(self):
        self._stores: dict[str, dict[str, KVEntry]] = defaultdict(dict)

    def set(self, sandbox_id: str, key: str, value: str,
            ttl: float = 0) -> dict:
        if len(key) > self.MAX_KEY_LENGTH:
            return {"ok": False, "error": "Key too long"}
        if len(value.encode()) > self.MAX_VALUE_SIZE:
            return {"ok": False, "error": "Value too large"}
        store = self._stores[sandbox_id]
        if key not in store and len(store) >= self.MAX_ENTRIES:
            return {"ok": False, "error": "Store full"}

        store[key] = KVEntry(key=key, value=value, ttl=ttl)
        return {"ok": True, "size_bytes": len(value.encode())}

    def get(self, sandbox_id: str, key: str) -> str | None:
        entry = self._stores.get(sandbox_id, {}).get(key)
        if not entry:
            return None
        if entry.is_expired:
            self._stores[sandbox_id].pop(key, None)
            return None
        return entry.value

    def delete(self, sandbox_id: str, key: str) -> bool:
        return self._stores.get(sandbox_id, {}).pop(key, None) is not None

    def exists(self, sandbox_id: str, key: str) -> bool:
        return self.get(sandbox_id, key) is not None

    def increment(self, sandbox_id: str, key: str, amount: int = 1) -> int | None:
        current = self.get(sandbox_id, key)
        try:
            val = int(current) if current else 0
        except ValueError:
            return None
        val += amount
        self.set(sandbox_id, key, str(val))
        return val

    def append(self, sandbox_id: str, key: str, suffix: str) -> int | None:
        current = self.get(sandbox_id, key) or ""
        new_val = current + suffix
        if len(new_val.encode()) > self.MAX_VALUE_SIZE:
            return None
        self.set(sandbox_id, key, new_val)
        return len(new_val)

    def scan(self, sandbox_id: str, prefix: str) -> list[str]:
        store = self._stores.get(sandbox_id, {})
        return sorted(k for k, v in store.items()
                      if k.startswith(prefix) and not v.is_expired)

    def count(self, sandbox_id: str) -> int:
        return len([k for k, v in self._stores.get(sandbox_id, {}).items()
                    if not v.is_expired])

    def clear(self, sandbox_id: str) -> int:
        count = len(self._stores.get(sandbox_id, {}))
        self._stores[sandbox_id] = {}
        return count
