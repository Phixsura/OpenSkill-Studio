"""App API Developer Webhook Fan-Out Manager — deliver events to multiple destinations."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class FanOutTarget:
    target_id: str
    destination: str
    event_types: list[str] = field(default_factory=list)
    enabled: bool = True
    delivery_count: int = 0
    failure_count: int = 0

@dataclass
class FanOutResult:
    event_type: str
    targets_matched: int
    targets_delivered: int
    targets_failed: int

class AppAPIDeveloperAPIWebhookFanOutManager:
    def __init__(self) -> None:
        self._targets: dict[tuple[str, str], FanOutTarget] = {}

    def add_target(self, installation_id: str, target_id: str, destination: str, event_types: list[str]) -> FanOutTarget:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, target_id)
        if key in self._targets: raise ValueError(f"Target {target_id} exists")
        t = FanOutTarget(target_id=target_id, destination=destination, event_types=event_types)
        self._targets[key] = t
        return t

    def fan_out(self, installation_id: str, event_type: str, results: dict[str, bool] | None = None) -> FanOutResult:
        targets = self._matching_targets(installation_id, event_type)
        delivered = failed = 0
        for t in targets:
            t.delivery_count += 1
            if results and not results.get(t.target_id, True):
                t.failure_count += 1
                failed += 1
            else:
                delivered += 1
        return FanOutResult(event_type=event_type, targets_matched=len(targets), targets_delivered=delivered, targets_failed=failed)

    def toggle(self, installation_id: str, target_id: str, enabled: bool) -> FanOutTarget:
        key = (installation_id, target_id)
        t = self._targets.get(key)
        if t is None: raise KeyError(f"Target {target_id} not found")
        t.enabled = enabled
        return t

    def list_targets(self, installation_id: str) -> list[FanOutTarget]:
        return [t for (inst, _), t in self._targets.items() if inst == installation_id]

    def _matching_targets(self, installation_id: str, event_type: str) -> list[FanOutTarget]:
        return [t for (inst, _), t in self._targets.items() if inst == installation_id and t.enabled and (not t.event_types or event_type in t.event_types)]
