"""App API Developer API Traffic Splitter — route traffic between API versions."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class TrafficRule:
    rule_id: str
    endpoint: str
    splits: dict[str, int]  # version -> weight (0-100)
    total_routed: int = 0
    per_version_count: dict[str, int] = field(default_factory=dict)

class AppAPIDeveloperAPIApiTrafficSplitter:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], TrafficRule] = {}

    def create_rule(self, installation_id: str, rule_id: str, endpoint: str, splits: dict[str, int]) -> TrafficRule:
        if not installation_id: raise ValueError("installation_id is required")
        total = sum(splits.values())
        if total != 100: raise ValueError(f"Splits must total 100, got {total}")
        key = (installation_id, rule_id)
        if key in self._rules: raise ValueError(f"Rule {rule_id} exists")
        r = TrafficRule(rule_id=rule_id, endpoint=endpoint, splits=splits, per_version_count={v: 0 for v in splits})
        self._rules[key] = r
        return r

    def route(self, installation_id: str, rule_id: str, request_id: str) -> str:
        r = self._get(installation_id, rule_id)
        h = int(hashlib.sha256(request_id.encode()).hexdigest()[:8], 16) % 100
        cumulative = 0
        for version, weight in r.splits.items():
            cumulative += weight
            if h < cumulative:
                r.total_routed += 1
                r.per_version_count[version] = r.per_version_count.get(version, 0) + 1
                return version
        # fallback to last version
        last = list(r.splits.keys())[-1]
        r.total_routed += 1
        r.per_version_count[last] = r.per_version_count.get(last, 0) + 1
        return last

    def stats(self, installation_id: str, rule_id: str) -> dict[str, int]:
        r = self._get(installation_id, rule_id)
        return dict(r.per_version_count)

    def list_rules(self, installation_id: str) -> list[TrafficRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def _get(self, installation_id: str, rule_id: str) -> TrafficRule:
        key = (installation_id, rule_id)
        r = self._rules.get(key)
        if r is None: raise KeyError(f"Rule {rule_id} not found")
        return r
