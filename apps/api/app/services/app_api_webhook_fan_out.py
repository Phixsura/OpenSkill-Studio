"""App API Webhook Fan Out — fan out events to multiple destinations."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class FanOutResult:
    event_type: str
    destinations: list[str]
    delivered: int = 0
    failed: int = 0

    @property
    def total(self) -> int:
        return self.delivered + self.failed

    @property
    def success_rate(self) -> float:
        if self.total == 0: return 100.0
        return round(self.delivered / self.total * 100, 1)

class AppAPIWebhookFanOut:
    def __init__(self) -> None:
        self._results: dict[str, list[FanOutResult]] = {}

    def fan_out(self, installation_id: str, event_type: str, destinations: list[str]) -> FanOutResult:
        if not installation_id: raise ValueError("installation_id is required")
        if not destinations: raise ValueError("at least one destination required")
        result = FanOutResult(event_type=event_type, destinations=list(destinations))
        self._results.setdefault(installation_id, []).append(result)
        return result

    def record_delivery(self, installation_id: str, index: int, success: bool) -> FanOutResult:
        results = self._results.get(installation_id, [])
        if index >= len(results): raise IndexError("Result not found")
        r = results[index]
        if success: r.delivered += 1
        else: r.failed += 1
        return r

    def recent(self, installation_id: str, limit: int = 20) -> list[FanOutResult]:
        return list(reversed(self._results.get(installation_id, [])[-limit:]))

    def total_fan_outs(self, installation_id: str) -> int:
        return len(self._results.get(installation_id, []))
