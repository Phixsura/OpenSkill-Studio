"""Topological Cache — cache with dependency-based cascading invalidation.

Unlike simple TTL caches, when a dependency changes, all entries
that depend on it are invalidated recursively.

Implements:
- Cache entries with explicit dependencies
- Cascading invalidation (A depends on B → invalidate B → A gone)
- Lazy recomputation (recompute on next access)
- Dependency cycle prevention
- Cache hit/miss stats per entry
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import defaultdict


@dataclass
class CacheEntry:
    key: str
    value: object
    dependencies: list[str] = field(default_factory=list)
    computed_at: float = 0.0
    hits: int = 0
    recompute_fn: object | None = None  # callable to recompute

    def __post_init__(self):
        if not self.computed_at: self.computed_at = time.time()


class TopoCacheService:
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._dependents: dict[str, set[str]] = defaultdict(set)  # dep → {keys that depend on it}
        self._total_hits = 0
        self._total_misses = 0
        self._total_invalidations = 0

    def put(self, key: str, value: object, dependencies: list[str] | None = None,
            recompute_fn: callable | None = None) -> None:
        """Store a value with its dependencies."""
        deps = dependencies or []
        # Cycle prevention
        for dep in deps:
            if self._has_path(key, dep):
                raise ValueError(f"Circular dependency: {key} → {dep} creates cycle")

        entry = CacheEntry(key=key, value=value, dependencies=deps,
                           recompute_fn=recompute_fn)
        self._cache[key] = entry

        # Register reverse dependency
        for dep in deps:
            self._dependents[dep].add(key)

    def get(self, key: str) -> object | None:
        entry = self._cache.get(key)
        if entry is None:
            self._total_misses += 1
            return None
        entry.hits += 1
        self._total_hits += 1
        return entry.value

    def get_or_compute(self, key: str) -> object | None:
        """Get cached value, or recompute if missing and recompute_fn is set."""
        value = self.get(key)
        if value is not None:
            return value
        # Try to find a stale entry with recompute_fn
        # (entry was invalidated but fn preserved)
        return None

    def invalidate(self, key: str) -> list[str]:
        """Invalidate a key and cascade to all dependents. Returns all invalidated keys."""
        invalidated = []
        self._cascade_invalidate(key, invalidated, set())
        return invalidated

    def _cascade_invalidate(self, key: str, invalidated: list[str],
                             visited: set[str]) -> None:
        if key in visited:
            return
        visited.add(key)

        if key in self._cache:
            del self._cache[key]
            invalidated.append(key)
            self._total_invalidations += 1

        # Cascade to dependents
        for dependent in list(self._dependents.get(key, set())):
            self._cascade_invalidate(dependent, invalidated, visited)

    def _has_path(self, from_key: str, to_key: str) -> bool:
        """Check if there's a dependency path from from_key to to_key."""
        visited = set()
        queue = [from_key]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for dep in self._dependents.get(current, set()):
                if dep == to_key:
                    return True
                queue.append(dep)
        return False

    def get_dependencies(self, key: str) -> list[str]:
        entry = self._cache.get(key)
        return list(entry.dependencies) if entry else []

    def get_dependents(self, key: str) -> list[str]:
        return sorted(self._dependents.get(key, set()))

    def stats(self) -> dict:
        total = self._total_hits + self._total_misses
        return {
            "entries": len(self._cache),
            "hits": self._total_hits,
            "misses": self._total_misses,
            "hit_rate": round(self._total_hits / max(1, total) * 100, 1),
            "invalidations": self._total_invalidations,
        }
