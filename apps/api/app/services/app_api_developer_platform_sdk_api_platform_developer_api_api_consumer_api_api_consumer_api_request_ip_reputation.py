"""API Consumer Request IP Reputation — track and score IP addresses by behavior."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class IpReputation:
    ip_address: str
    score: int = 100  # 0-100, 100=trusted
    total_requests: int = 0
    blocked_requests: int = 0
    suspicious_events: int = 0

    @property
    def tier(self) -> str:
        if self.score >= 80: return "trusted"
        if self.score >= 50: return "neutral"
        if self.score >= 20: return "suspicious"
        return "blocked"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputation:
    def __init__(self) -> None:
        self._reputations: dict[tuple[str, str], IpReputation] = {}

    def get_or_create(self, installation_id: str, ip_address: str) -> IpReputation:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, ip_address)
        if key not in self._reputations:
            self._reputations[key] = IpReputation(ip_address=ip_address)
        return self._reputations[key]

    def record_request(self, installation_id: str, ip_address: str, blocked: bool = False, suspicious: bool = False) -> IpReputation:
        rep = self.get_or_create(installation_id, ip_address)
        rep.total_requests += 1
        if blocked: rep.blocked_requests += 1; rep.score = max(0, rep.score - 5)
        if suspicious: rep.suspicious_events += 1; rep.score = max(0, rep.score - 10)
        return rep

    def should_block(self, installation_id: str, ip_address: str) -> bool:
        rep = self._reputations.get((installation_id, ip_address))
        return rep is not None and rep.tier == "blocked"

    def suspicious_ips(self, installation_id: str) -> list[IpReputation]:
        return [r for (inst, _), r in self._reputations.items() if inst == installation_id and r.tier in ("suspicious", "blocked")]

    def list_reputations(self, installation_id: str) -> list[IpReputation]:
        return [r for (inst, _), r in self._reputations.items() if inst == installation_id]
