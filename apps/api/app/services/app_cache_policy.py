"""App Cache Policy — manage caching rules for API responses.

Manages cache policies:
- Define TTL-based cache rules per endpoint
- Cache hit/miss tracking
- Invalidation by pattern
- Per-installation scoped policies
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class CacheRule:
    """A cache policy rule."""

    rule_id: str
    path_pattern: str  # e.g., "/api/v1/users/*"
    ttl_seconds: int
    methods: list[str] = field(default_factory=lambda: ["GET"])
    enabled: bool = True
    hits: int = 0
    misses: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(self.hits / total * 100, 1)


@dataclass
class CacheEntry:
    """A cached response."""

    key: str
    stored_at: float
    ttl_seconds: int

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.stored_at) > self.ttl_seconds


class AppCachePolicy:
    """Manage caching rules for API responses."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], CacheRule] = {}
        self._cache: dict[tuple[str, str], CacheEntry] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, path_pattern: str,
        ttl_seconds: int, methods: list[str] | None = None,
    ) -> CacheRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")

        rule = CacheRule(
            rule_id=rule_id, path_pattern=path_pattern,
            ttl_seconds=ttl_seconds, methods=methods or ["GET"],
        )
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def lookup(
        self, installation_id: str, method: str, path: str,
    ) -> CacheRule | None:
        """Find matching cache rule for a request."""
        for (inst, _), rule in self._rules.items():
            if inst != installation_id or not rule.enabled:
                continue
            if method.upper() not in rule.methods:
                continue
            if self._path_matches(rule.path_pattern, path):
                return rule
        return None

    def record_hit(self, installation_id: str, rule_id: str) -> CacheRule:
        r = self._get(installation_id, rule_id)
        r.hits += 1
        return r

    def record_miss(self, installation_id: str, rule_id: str) -> CacheRule:
        r = self._get(installation_id, rule_id)
        r.misses += 1
        return r

    def invalidate(self, installation_id: str, path_pattern: str) -> int:
        """Invalidate cache entries matching pattern. Returns count."""
        count = 0
        to_remove = []
        for (inst, key), entry in self._cache.items():
            if inst == installation_id and self._path_matches(path_pattern, key):
                to_remove.append((inst, key))
                count += 1
        for k in to_remove:
            del self._cache[k]
        return count

    def list_rules(self, installation_id: str) -> list[CacheRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def toggle(self, installation_id: str, rule_id: str, enabled: bool) -> CacheRule:
        r = self._get(installation_id, rule_id)
        r.enabled = enabled
        return r

    def _get(self, installation_id: str, rule_id: str) -> CacheRule:
        key = (installation_id, rule_id)
        r = self._rules.get(key)
        if r is None:
            raise KeyError(f"Rule {rule_id} not found")
        return r

    def _path_matches(self, pattern: str, path: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith("/*"):
            return path.startswith(pattern[:-1])
        return pattern == path
