"""App API Developer Consumer IP Tracker — track API access by consumer IP."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class IPAccessRecord:
    consumer_id: str
    ips: dict[str, int] = field(default_factory=dict)  # ip -> request count
    last_seen_at: float = 0.0

    @property
    def unique_ip_count(self) -> int:
        return len(self.ips)

    @property
    def total_requests(self) -> int:
        return sum(self.ips.values())

    @property
    def top_ip(self) -> str:
        if not self.ips: return ""
        return max(self.ips, key=self.ips.get)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTracker:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], IPAccessRecord] = {}

    def track(self, installation_id: str, consumer_id: str, ip_address: str) -> IPAccessRecord:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._records:
            self._records[key] = IPAccessRecord(consumer_id=consumer_id)
        r = self._records[key]
        r.ips[ip_address] = r.ips.get(ip_address, 0) + 1
        r.last_seen_at = time.time()
        return r

    def get(self, installation_id: str, consumer_id: str) -> IPAccessRecord | None:
        return self._records.get((installation_id, consumer_id))

    def suspicious_consumers(self, installation_id: str, max_ips: int = 10) -> list[IPAccessRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id and r.unique_ip_count > max_ips]

    def all_records(self, installation_id: str) -> list[IPAccessRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id]
