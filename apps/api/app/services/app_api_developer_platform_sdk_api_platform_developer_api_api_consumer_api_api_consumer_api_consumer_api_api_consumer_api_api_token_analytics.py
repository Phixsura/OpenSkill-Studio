"""Consumer API Token Analytics — track and analyze API token usage patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class TokenUsageRecord:
    token_id: str
    consumer_id: str
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime
    ip_address: str = ""

@dataclass
class TokenAnalytics:
    token_id: str
    total_requests: int
    unique_endpoints: int
    unique_ips: int
    error_count: int
    last_used_at: datetime | None = None
    top_endpoints: list[tuple[str, int]] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str], list[TokenUsageRecord]] = {}  # (inst, consumer, token)

    def record(self, installation_id: str, record: TokenUsageRecord) -> TokenUsageRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, record.consumer_id, record.token_id)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(record)
        if len(self._records[key]) > 10000:
            self._records[key] = self._records[key][-10000:]
        return record

    def get_analytics(self, installation_id: str, consumer_id: str, token_id: str) -> TokenAnalytics:
        records = self._records.get((installation_id, consumer_id, token_id), [])
        if not records:
            return TokenAnalytics(token_id=token_id, total_requests=0, unique_endpoints=0, unique_ips=0, error_count=0)
        endpoints: dict[str, int] = {}
        ips: set[str] = set()
        errors = 0
        for r in records:
            ep_key = f"{r.method} {r.endpoint}"
            endpoints[ep_key] = endpoints.get(ep_key, 0) + 1
            if r.ip_address:
                ips.add(r.ip_address)
            if r.status_code >= 400:
                errors += 1
        top = sorted(endpoints.items(), key=lambda x: -x[1])[:5]
        return TokenAnalytics(token_id=token_id, total_requests=len(records), unique_endpoints=len(endpoints), unique_ips=len(ips), error_count=errors, last_used_at=records[-1].timestamp, top_endpoints=top)

    def detect_anomaly(self, installation_id: str, consumer_id: str, token_id: str, window_hours: int = 1, now: datetime | None = None) -> dict[str, bool]:
        now = now or datetime.utcnow()
        records = self._records.get((installation_id, consumer_id, token_id), [])
        cutoff = now - timedelta(hours=window_hours)
        recent = [r for r in records if r.timestamp >= cutoff]
        older = [r for r in records if r.timestamp < cutoff]
        recent_ips = {r.ip_address for r in recent if r.ip_address}
        older_ips = {r.ip_address for r in older if r.ip_address}
        new_ips = recent_ips - older_ips
        return {"new_ips_detected": len(new_ips) > 0, "new_ip_count": len(new_ips), "recent_requests": len(recent), "high_error_rate": sum(1 for r in recent if r.status_code >= 400) / max(len(recent), 1) > 0.5}
