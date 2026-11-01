"""App API Developer Consumer SLA Tier — manage SLA tiers per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

SLA_TIERS = {
    "platinum": {"uptime": 99.99, "latency_p99_ms": 100, "support_response_hours": 1},
    "gold": {"uptime": 99.9, "latency_p99_ms": 200, "support_response_hours": 4},
    "silver": {"uptime": 99.5, "latency_p99_ms": 500, "support_response_hours": 8},
    "bronze": {"uptime": 99.0, "latency_p99_ms": 1000, "support_response_hours": 24},
}

@dataclass
class ConsumerSLATier:
    consumer_id: str
    tier: str
    uptime_target: float
    latency_target_ms: int
    support_hours: int
    actual_uptime: float = 100.0
    actual_latency_ms: int = 0

    @property
    def meeting_sla(self) -> bool:
        return self.actual_uptime >= self.uptime_target and self.actual_latency_ms <= self.latency_target_ms

class AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier:
    def __init__(self) -> None:
        self._tiers: dict[tuple[str, str], ConsumerSLATier] = {}

    def assign(self, installation_id: str, consumer_id: str, tier: str) -> ConsumerSLATier:
        if not installation_id: raise ValueError("installation_id is required")
        if tier not in SLA_TIERS: raise ValueError(f"Invalid tier: {tier}")
        t = SLA_TIERS[tier]
        key = (installation_id, consumer_id)
        c = ConsumerSLATier(consumer_id=consumer_id, tier=tier, uptime_target=t["uptime"], latency_target_ms=t["latency_p99_ms"], support_hours=t["support_response_hours"])
        self._tiers[key] = c
        return c

    def update_actuals(self, installation_id: str, consumer_id: str, uptime: float, latency_ms: int) -> ConsumerSLATier:
        key = (installation_id, consumer_id)
        c = self._tiers.get(key)
        if c is None: raise KeyError(f"No SLA for {consumer_id}")
        c.actual_uptime = uptime
        c.actual_latency_ms = latency_ms
        return c

    def breaching(self, installation_id: str) -> list[ConsumerSLATier]:
        return [c for (inst, _), c in self._tiers.items() if inst == installation_id and not c.meeting_sla]

    def by_tier(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), c in self._tiers.items():
            if inst == installation_id: counts[c.tier] = counts.get(c.tier, 0) + 1
        return counts

    def all_consumers(self, installation_id: str) -> list[ConsumerSLATier]:
        return [c for (inst, _), c in self._tiers.items() if inst == installation_id]
