"""App Content Store — key-value content storage for installed apps.

Manages versioned content blobs for installed apps:
- CRUD operations with content type tracking
- Version history per key
- Size tracking and quota enforcement
- Per-installation scoped storage
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ContentEntry:
    """A versioned content entry."""

    key: str
    content: str
    content_type: str  # e.g. "text/html", "application/json"
    size_bytes: int
    version: int
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class AppContentStore:
    """Key-value content storage for installed apps."""

    def __init__(self, max_size_bytes: int = 10 * 1024 * 1024) -> None:
        # (installation_id, key) → ContentEntry
        self._entries: dict[tuple[str, str], ContentEntry] = {}
        # (installation_id, key) → list of past versions
        self._history: dict[tuple[str, str], list[ContentEntry]] = {}
        self._max_size = max_size_bytes

    def put(
        self,
        installation_id: str,
        key: str,
        content: str,
        content_type: str = "text/plain",
        now: float | None = None,
    ) -> ContentEntry:
        """Create or update content."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not key:
            raise ValueError("key is required")
        if not content_type:
            raise ValueError("content_type is required")

        size = len(content.encode("utf-8"))
        total = self._total_size(installation_id) - self._entry_size(installation_id, key) + size
        if total > self._max_size:
            raise ValueError("Storage quota exceeded")

        compound = (installation_id, key)
        now = now or time.time()
        existing = self._entries.get(compound)
        version = (existing.version + 1) if existing else 1

        # Archive old version
        if existing:
            self._history.setdefault(compound, []).append(existing)

        entry = ContentEntry(
            key=key,
            content=content,
            content_type=content_type,
            size_bytes=size,
            version=version,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        self._entries[compound] = entry
        return entry

    def get(self, installation_id: str, key: str) -> ContentEntry | None:
        return self._entries.get((installation_id, key))

    def delete(self, installation_id: str, key: str) -> bool:
        compound = (installation_id, key)
        if compound in self._entries:
            del self._entries[compound]
            self._history.pop(compound, None)
            return True
        return False

    def list_keys(self, installation_id: str) -> list[str]:
        return sorted(
            key for (inst, key) in self._entries if inst == installation_id
        )

    def get_history(
        self, installation_id: str, key: str, limit: int = 10
    ) -> list[ContentEntry]:
        """Get version history, newest first."""
        compound = (installation_id, key)
        history = self._history.get(compound, [])
        return list(reversed(history[-limit:]))

    def total_size(self, installation_id: str) -> int:
        return self._total_size(installation_id)

    def entry_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._entries if inst == installation_id)

    def _total_size(self, installation_id: str) -> int:
        return sum(
            e.size_bytes for (inst, _), e in self._entries.items()
            if inst == installation_id
        )

    def _entry_size(self, installation_id: str, key: str) -> int:
        entry = self._entries.get((installation_id, key))
        return entry.size_bytes if entry else 0
