"""App API Developer Endpoint Cache Invalidation — manage cache invalidation rules."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class CacheInvalidationRule:
    rule_id: str
    endpoint: str
    trigger: str  # "on_write", "on_delete", "ttl_expired", "manual"
    pattern: str = "*"  # cache key pattern to invalidate
    invalidations: int = 0
    last_triggered_at: float = 0.0

class AppAPIDeveloperPlatformSDKApiEndpointCacheInvalidation:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], CacheInvalidationRule] = {}

    def add_rule(self, installation_id: str, rule_id: str, endpoint: str, trigger: str, pattern: str = "*") -> CacheInvalidationRule:
        if not installation_id: raise ValueError("installation_id is required")
        if trigger not in ("on_write", "on_delete", "ttl_expired", "manual"): raise ValueError("invalid trigger")
        key = (installation_id, rule_id)
        if key in self._rules: raise ValueError(f"Rule {rule_id} exists")
        r = CacheInvalidationRule(rule_id=rule_id, endpoint=endpoint, trigger=trigger, pattern=pattern)
        self._rules[key] = r
        return r

    def trigger(self, installation_id: str, endpoint: str, trigger_type: str) -> list[CacheInvalidationRule]:
        triggered = []
        for (inst, _), r in self._rules.items():
            if inst == installation_id and r.endpoint == endpoint and r.trigger == trigger_type:
                r.invalidations += 1
                r.last_triggered_at = time.time()
                triggered.append(r)
        return triggered

    def all_rules(self, installation_id: str) -> list[CacheInvalidationRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def most_triggered(self, installation_id: str, limit: int = 5) -> list[CacheInvalidationRule]:
        rules = self.all_rules(installation_id)
        return sorted(rules, key=lambda r: r.invalidations, reverse=True)[:limit]
