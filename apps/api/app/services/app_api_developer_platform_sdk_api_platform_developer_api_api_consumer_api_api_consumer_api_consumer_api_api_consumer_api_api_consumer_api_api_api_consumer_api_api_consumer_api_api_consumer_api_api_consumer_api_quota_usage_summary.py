"""Consumer API Quota Usage Summary — unified quota usage across all resource types."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class QuotaUsage:
    resource: str
    used: int
    limit: int
    usage_pct: float
    status: str  # "ok", "warning", "exceeded"

@dataclass
class QuotaUsageSummary:
    consumer_id: str
    quotas: list[QuotaUsage] = field(default_factory=list)
    overall_status: str = "ok"
    total_resources: int = 0
    at_risk_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str, str], tuple[int, int]] = {}  # (inst, consumer, resource) -> (used, limit)

    def set_usage(self, installation_id: str, consumer_id: str, resource: str, used: int, limit: int) -> QuotaUsage:
        if not installation_id:
            raise ValueError("installation_id is required")
        if used < 0 or limit < 0:
            raise ValueError("Values must be non-negative")
        self._usage[(installation_id, consumer_id, resource)] = (used, limit)
        pct = (used / limit * 100) if limit > 0 else 0
        status = "exceeded" if used > limit else ("warning" if pct >= 80 else "ok")
        return QuotaUsage(resource=resource, used=used, limit=limit, usage_pct=round(pct, 1), status=status)

    def get_summary(self, installation_id: str, consumer_id: str) -> QuotaUsageSummary:
        quotas: list[QuotaUsage] = []
        for (inst, cid, resource), (used, limit) in self._usage.items():
            if inst != installation_id or cid != consumer_id:
                continue
            pct = (used / limit * 100) if limit > 0 else 0
            status = "exceeded" if used > limit else ("warning" if pct >= 80 else "ok")
            quotas.append(QuotaUsage(resource=resource, used=used, limit=limit, usage_pct=round(pct, 1), status=status))
        quotas.sort(key=lambda q: -q.usage_pct)
        at_risk = sum(1 for q in quotas if q.status != "ok")
        overall = "exceeded" if any(q.status == "exceeded" for q in quotas) else ("warning" if at_risk > 0 else "ok")
        return QuotaUsageSummary(consumer_id=consumer_id, quotas=quotas, overall_status=overall, total_resources=len(quotas), at_risk_count=at_risk)
