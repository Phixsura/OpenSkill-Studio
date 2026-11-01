"""Consumer API IP Allowlist — manage consumer-level IP access control."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import ipaddress
import structlog

log = structlog.get_logger()

@dataclass
class IPEntry:
    entry_id: str
    cidr: str
    label: str = ""
    added_at: datetime | None = None
    added_by: str = ""

@dataclass
class IPCheckResult:
    allowed: bool
    ip: str
    matched_entry: IPEntry | None = None
    reason: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist:
    def __init__(self) -> None:
        self._lists: dict[tuple[str, str], list[IPEntry]] = {}  # (inst, consumer)

    def add_entry(self, installation_id: str, consumer_id: str, entry: IPEntry) -> IPEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        try:
            ipaddress.ip_network(entry.cidr, strict=False)
        except ValueError:
            raise ValueError(f"Invalid CIDR: {entry.cidr}")
        entry.added_at = entry.added_at or datetime.utcnow()
        key = (installation_id, consumer_id)
        if key not in self._lists:
            self._lists[key] = []
        # Check duplicate
        for existing in self._lists[key]:
            if existing.cidr == entry.cidr:
                raise ValueError(f"CIDR {entry.cidr} already in allowlist")
        self._lists[key].append(entry)
        return entry

    def remove_entry(self, installation_id: str, consumer_id: str, entry_id: str) -> None:
        key = (installation_id, consumer_id)
        entries = self._lists.get(key, [])
        before = len(entries)
        self._lists[key] = [e for e in entries if e.entry_id != entry_id]
        if len(self._lists[key]) == before:
            raise ValueError("Entry not found")

    def check(self, installation_id: str, consumer_id: str, ip: str) -> IPCheckResult:
        key = (installation_id, consumer_id)
        entries = self._lists.get(key)
        if not entries:
            return IPCheckResult(allowed=True, ip=ip, reason="no_allowlist")
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return IPCheckResult(allowed=False, ip=ip, reason="invalid_ip")
        for entry in entries:
            net = ipaddress.ip_network(entry.cidr, strict=False)
            if addr in net:
                return IPCheckResult(allowed=True, ip=ip, matched_entry=entry, reason="allowed")
        return IPCheckResult(allowed=False, ip=ip, reason="not_in_allowlist")

    def list_entries(self, installation_id: str, consumer_id: str) -> list[IPEntry]:
        return self._lists.get((installation_id, consumer_id), [])
