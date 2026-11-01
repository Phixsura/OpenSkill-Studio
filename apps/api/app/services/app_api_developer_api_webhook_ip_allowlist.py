"""App API Developer Webhook IP Allowlist — restrict webhook sources by IP."""
from __future__ import annotations
from dataclasses import dataclass, field
import ipaddress
import structlog

log = structlog.get_logger()

@dataclass
class IPAllowlist:
    allowlist_id: str
    entries: list[str] = field(default_factory=list)  # IPs or CIDRs
    blocked_count: int = 0
    allowed_count: int = 0

class AppAPIDeveloperAPIWebhookIPAllowlist:
    def __init__(self) -> None:
        self._lists: dict[tuple[str, str], IPAllowlist] = {}

    def create(self, installation_id: str, allowlist_id: str, entries: list[str]) -> IPAllowlist:
        if not installation_id: raise ValueError("installation_id is required")
        for entry in entries:
            try:
                ipaddress.ip_network(entry, strict=False)
            except ValueError:
                raise ValueError(f"Invalid IP/CIDR: {entry}")
        key = (installation_id, allowlist_id)
        if key in self._lists: raise ValueError(f"Allowlist {allowlist_id} exists")
        al = IPAllowlist(allowlist_id=allowlist_id, entries=entries)
        self._lists[key] = al
        return al

    def check(self, installation_id: str, allowlist_id: str, ip: str) -> bool:
        al = self._get(installation_id, allowlist_id)
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            al.blocked_count += 1
            return False
        for entry in al.entries:
            net = ipaddress.ip_network(entry, strict=False)
            if addr in net:
                al.allowed_count += 1
                return True
        al.blocked_count += 1
        return False

    def add_entry(self, installation_id: str, allowlist_id: str, entry: str) -> IPAllowlist:
        ipaddress.ip_network(entry, strict=False)  # validate
        al = self._get(installation_id, allowlist_id)
        if entry not in al.entries:
            al.entries.append(entry)
        return al

    def stats(self, installation_id: str, allowlist_id: str) -> dict[str, int]:
        al = self._get(installation_id, allowlist_id)
        return {"allowed": al.allowed_count, "blocked": al.blocked_count, "entries": len(al.entries)}

    def _get(self, installation_id: str, allowlist_id: str) -> IPAllowlist:
        key = (installation_id, allowlist_id)
        al = self._lists.get(key)
        if al is None: raise KeyError(f"Allowlist {allowlist_id} not found")
        return al
