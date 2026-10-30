"""Consumer SLA Tier — assign and enforce SLA tiers with guaranteed metrics."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SLATier:
    tier_id: str
    name: str
    uptime_pct: float         # e.g. 99.9
    max_latency_ms: int       # p99 latency guarantee
    max_error_rate_pct: float  # e.g. 0.1
    support_response_hours: int = 24
    priority: int = 0         # higher = better tier

@dataclass
class SLAAssignment:
    consumer_id: str
    tier_id: str
    effective_from: str  # ISO date

@dataclass
class SLAComplianceResult:
    tier_name: str
    uptime_compliant: bool
    latency_compliant: bool
    error_rate_compliant: bool
    overall_compliant: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSlaTier:
    def __init__(self) -> None:
        self._tiers: dict[tuple[str, str], SLATier] = {}
        self._assignments: dict[tuple[str, str], SLAAssignment] = {}

    def define_tier(self, installation_id: str, tier: SLATier) -> SLATier:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0 < tier.uptime_pct <= 100):
            raise ValueError("uptime_pct must be between 0 and 100")
        self._tiers[(installation_id, tier.tier_id)] = tier
        log.info("sla_tier_defined", installation_id=installation_id, tier=tier.name)
        return tier

    def assign(self, installation_id: str, assignment: SLAAssignment) -> SLAAssignment:
        if (installation_id, assignment.tier_id) not in self._tiers:
            raise ValueError(f"Tier {assignment.tier_id} not found")
        self._assignments[(installation_id, assignment.consumer_id)] = assignment
        return assignment

    def get_tier(self, installation_id: str, consumer_id: str) -> SLATier | None:
        assignment = self._assignments.get((installation_id, consumer_id))
        if not assignment:
            return None
        return self._tiers.get((installation_id, assignment.tier_id))

    def check_compliance(self, installation_id: str, consumer_id: str, actual_uptime: float, actual_latency_ms: int, actual_error_rate: float) -> SLAComplianceResult:
        tier = self.get_tier(installation_id, consumer_id)
        if not tier:
            raise ValueError("No SLA tier assigned")
        up = actual_uptime >= tier.uptime_pct
        lat = actual_latency_ms <= tier.max_latency_ms
        err = actual_error_rate <= tier.max_error_rate_pct
        return SLAComplianceResult(tier_name=tier.name, uptime_compliant=up, latency_compliant=lat, error_rate_compliant=err, overall_compliant=up and lat and err)

    def list_tiers(self, installation_id: str) -> list[SLATier]:
        return sorted([t for (inst, _), t in self._tiers.items() if inst == installation_id], key=lambda t: t.priority, reverse=True)
