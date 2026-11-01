"""Consumer API Usage Quota Dashboard — unified quota and usage overview."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class QuotaItem:
    name: str
    used: int
    limit: int
    category: str  # "requests", "resources", "storage", "compute"

@dataclass
class UsageQuotaDashboard:
    consumer_id: str
    items: list[QuotaItem] = field(default_factory=list)
    overall_usage_pct: float = 0.0
    items_at_risk: int = 0
    items_exceeded: int = 0

VALID_CATEGORIES = {"requests", "resources", "storage", "compute", "bandwidth"}

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str, str], QuotaItem] = {}

    def set_quota(self, installation_id: str, consumer_id: str, item: QuotaItem) -> QuotaItem:
        if not installation_id:
            raise ValueError("installation_id is required")
        if item.category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {item.category}")
        if item.limit < 0:
            raise ValueError("limit must be non-negative")
        self._items[(installation_id, consumer_id, item.name)] = item
        return item

    def update_usage(self, installation_id: str, consumer_id: str, name: str, used: int) -> QuotaItem:
        key = (installation_id, consumer_id, name)
        item = self._items.get(key)
        if not item:
            raise ValueError(f"Quota {name} not found")
        if used < 0:
            raise ValueError("used must be non-negative")
        item.used = used
        return item

    def get_dashboard(self, installation_id: str, consumer_id: str) -> UsageQuotaDashboard:
        items = [i for (inst, cid, _), i in self._items.items() if inst == installation_id and cid == consumer_id]
        if not items:
            return UsageQuotaDashboard(consumer_id=consumer_id)
        total_pct_sum = 0
        at_risk = 0
        exceeded = 0
        for i in items:
            pct = (i.used / max(i.limit, 1)) * 100
            total_pct_sum += pct
            if pct >= 100:
                exceeded += 1
            elif pct >= 80:
                at_risk += 1
        overall = round(total_pct_sum / len(items), 1)
        sorted_items = sorted(items, key=lambda i: -(i.used / max(i.limit, 1)))
        return UsageQuotaDashboard(consumer_id=consumer_id, items=sorted_items, overall_usage_pct=overall, items_at_risk=at_risk, items_exceeded=exceeded)
