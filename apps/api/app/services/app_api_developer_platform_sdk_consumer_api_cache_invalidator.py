"""Endpoint Cache Invalidator — tag-based cache invalidation with cascade."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class CacheEntry:
    key: str
    tags: set[str] = field(default_factory=set)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ttl_seconds: int = 300


@dataclass
class CacheInvalidator:
    """Tag-based cache invalidation with cascade support."""

    _entries: dict[str, CacheEntry] = field(default_factory=dict)
    _tag_index: dict[str, set[str]] = field(default_factory=dict)  # tag -> keys
    _cascades: dict[str, set[str]] = field(default_factory=dict)  # tag -> dependent tags
    _invalidation_log: list[dict] = field(default_factory=list)

    def register(self, key: str, tags: list[str], ttl_seconds: int = 300) -> dict:
        tag_set = set(tags)
        self._entries[key] = CacheEntry(key=key, tags=tag_set, ttl_seconds=ttl_seconds)
        for tag in tag_set:
            self._tag_index.setdefault(tag, set()).add(key)
        return {"key": key, "tags": sorted(tag_set), "total_entries": len(self._entries)}

    def add_cascade(self, tag: str, depends_on: str) -> dict:
        if tag == depends_on:
            raise ValueError("Tag cannot cascade to itself")
        self._cascades.setdefault(depends_on, set()).add(tag)
        logger.info("cascade_added", from_tag=depends_on, to_tag=tag)
        return {"from": depends_on, "to": tag}

    def invalidate_key(self, key: str) -> dict:
        entry = self._entries.pop(key, None)
        if not entry:
            return {"invalidated": 0}
        for tag in entry.tags:
            self._tag_index.get(tag, set()).discard(key)
        self._invalidation_log.append({"type": "key", "key": key,
                                        "timestamp": datetime.now(timezone.utc).isoformat()})
        return {"invalidated": 1, "key": key}

    def invalidate_tag(self, tag: str, visited: set[str] | None = None) -> dict:
        if visited is None:
            visited = set()
        if tag in visited:
            return {"invalidated": 0, "tag": tag, "reason": "cycle"}
        visited.add(tag)
        keys = list(self._tag_index.get(tag, set()))
        invalidated = 0
        for key in keys:
            entry = self._entries.pop(key, None)
            if entry:
                for t in entry.tags:
                    self._tag_index.get(t, set()).discard(key)
                invalidated += 1
        # Cascade
        cascade_tags = self._cascades.get(tag, set())
        for dep_tag in cascade_tags:
            result = self.invalidate_tag(dep_tag, visited)
            invalidated += result.get("invalidated", 0)
        self._invalidation_log.append({"type": "tag", "tag": tag, "count": invalidated,
                                        "timestamp": datetime.now(timezone.utc).isoformat()})
        logger.info("tag_invalidated", tag=tag, count=invalidated)
        return {"invalidated": invalidated, "tag": tag}

    def get_keys_by_tag(self, tag: str) -> list[str]:
        return sorted(self._tag_index.get(tag, set()))

    def get_stats(self) -> dict:
        return {
            "total_entries": len(self._entries),
            "total_tags": len(self._tag_index),
            "cascade_rules": sum(len(v) for v in self._cascades.values()),
            "total_invalidations": len(self._invalidation_log),
        }

    def get_entry(self, key: str) -> dict | None:
        entry = self._entries.get(key)
        if not entry:
            return None
        return {"key": entry.key, "tags": sorted(entry.tags), "ttl": entry.ttl_seconds}

    def clear_all(self) -> dict:
        count = len(self._entries)
        self._entries.clear()
        self._tag_index.clear()
        return {"cleared": count}
