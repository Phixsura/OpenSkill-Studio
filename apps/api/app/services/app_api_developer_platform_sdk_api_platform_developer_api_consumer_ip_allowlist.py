"""API Consumer IP Allowlist — restrict API access by source IP."""
from __future__ import annotations
from dataclasses import dataclass, field
import ipaddress
import time
import structlog

log = structlog.get_logger()

@dataclass
class IpEntry:
    entry_id: str
    network: str  # CIDR or single IP
    label: str = ""
    added_at: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist:
    def __init__(self) -> None:
        self._lists: dict[tuple[str, str], list[IpEntry]] = {}

    def add_entry(self, installation_id: str, consumer_id: str, entry: IpEntry) -> IpEntry:
        if not installation_id: raise ValueError("installation_id is required")
        try:
            ipaddress.ip_network(entry.network, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid network: {e}") from e
        self._lists.setdefault((installation_id, consumer_id), []).append(entry)
        return entry

    def check_ip(self, installation_id: str, consumer_id: str, ip: str) -> bool:
        entries = self._lists.get((installation_id, consumer_id))
        if entries is None: return True  # no allowlist = allow all
        if not entries: return True
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        for e in entries:
            net = ipaddress.ip_network(e.network, strict=False)
            if addr in net: return True
        return False

    def remove_entry(self, installation_id: str, consumer_id: str, entry_id: str) -> bool:
        entries = self._lists.get((installation_id, consumer_id), [])
        for i, e in enumerate(entries):
            if e.entry_id == entry_id:
                entries.pop(i)
                return True
        return False

    def list_entries(self, installation_id: str, consumer_id: str) -> list[IpEntry]:
        return self._lists.get((installation_id, consumer_id), [])

    def consumer_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._lists if inst == installation_id)
