"""Endpoint Rate Limit Tier — assign tiered rate limits per endpoint per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitTier:
    tier_id: str
    name: str
    requests_per_second: int
    requests_per_minute: int
    requests_per_hour: int
    burst_size: int = 0  # 0 = no burst

@dataclass
class TierAssignment:
    consumer_id: str
    endpoint_path: str
    tier_id: str

@dataclass
class RateLimitCheck:
    allowed: bool
    tier_name: str
    remaining_second: int
    remaining_minute: int
    retry_after_ms: int | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointRateLimitTier:
    def __init__(self) -> None:
        self._tiers: dict[tuple[str, str], RateLimitTier] = {}
        self._assignments: dict[tuple[str, str, str], TierAssignment] = {}  # (inst, consumer, path)
        self._counters: dict[tuple[str, str, str, str], int] = {}  # (inst, consumer, path, window) -> count

    def define_tier(self, installation_id: str, tier: RateLimitTier) -> RateLimitTier:
        if not installation_id:
            raise ValueError("installation_id is required")
        if tier.requests_per_second < 1:
            raise ValueError("requests_per_second must be positive")
        self._tiers[(installation_id, tier.tier_id)] = tier
        return tier

    def assign_tier(self, installation_id: str, assignment: TierAssignment) -> TierAssignment:
        if (installation_id, assignment.tier_id) not in self._tiers:
            raise ValueError(f"Tier {assignment.tier_id} not found")
        self._assignments[(installation_id, assignment.consumer_id, assignment.endpoint_path)] = assignment
        return assignment

    def check_and_consume(self, installation_id: str, consumer_id: str, endpoint_path: str, now: datetime) -> RateLimitCheck:
        asgn = self._assignments.get((installation_id, consumer_id, endpoint_path))
        if not asgn:
            return RateLimitCheck(allowed=True, tier_name="none", remaining_second=999, remaining_minute=999)
        tier = self._tiers.get((installation_id, asgn.tier_id))
        if not tier:
            return RateLimitCheck(allowed=True, tier_name="unknown", remaining_second=999, remaining_minute=999)
        sec_key = (installation_id, consumer_id, endpoint_path, f"s:{now.strftime('%H%M%S')}")
        min_key = (installation_id, consumer_id, endpoint_path, f"m:{now.strftime('%H%M')}")
        sec_count = self._counters.get(sec_key, 0)
        min_count = self._counters.get(min_key, 0)
        effective_rps = tier.requests_per_second + tier.burst_size
        if sec_count >= effective_rps:
            return RateLimitCheck(allowed=False, tier_name=tier.name, remaining_second=0, remaining_minute=max(0, tier.requests_per_minute - min_count), retry_after_ms=1000)
        if min_count >= tier.requests_per_minute:
            return RateLimitCheck(allowed=False, tier_name=tier.name, remaining_second=0, remaining_minute=0, retry_after_ms=60000)
        self._counters[sec_key] = sec_count + 1
        self._counters[min_key] = min_count + 1
        return RateLimitCheck(allowed=True, tier_name=tier.name, remaining_second=effective_rps - sec_count - 1, remaining_minute=tier.requests_per_minute - min_count - 1)

    def list_tiers(self, installation_id: str) -> list[RateLimitTier]:
        return sorted([t for (inst, _), t in self._tiers.items() if inst == installation_id], key=lambda t: t.requests_per_second)
