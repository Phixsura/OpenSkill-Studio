"""App IP Allowlist — manage IP-based access control.

Manages IP allowlists for installed apps:
- Add/remove CIDR ranges or individual IPs
- Check if an IP is allowed
- Temporary allowlist entries with expiration
- Per-installation scoped lists
"""

from __future__ import annotations

import ipaddress
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class AllowlistEntry:
    """An IP allowlist entry."""

    entry_id: str
    cidr: str
    label: str = ""
    expires_at: float | None = None
    created_at: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class AppIPAllowlist:
    """Manage IP-based access control."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], AllowlistEntry] = {}

    def add(
        self, installation_id: str, entry_id: str, cidr: str,
        label: str = "", ttl_seconds: int | None = None,
    ) -> AllowlistEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not entry_id:
            raise ValueError("entry_id is required")

        # Validate CIDR/IP
        try:
            ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            raise ValueError(f"Invalid CIDR: {cidr}")

        expires_at = None
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be positive")
            expires_at = time.time() + ttl_seconds

        entry = AllowlistEntry(
            entry_id=entry_id, cidr=cidr, label=label, expires_at=expires_at,
        )
        self._entries[(installation_id, entry_id)] = entry
        return entry

    def is_allowed(self, installation_id: str, ip: str) -> bool:
        """Check if an IP is in the allowlist."""
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False

        entries = [
            e for (inst, _), e in self._entries.items()
            if inst == installation_id and not e.is_expired
        ]

        if not entries:
            return False  # empty allowlist = deny all

        for entry in entries:
            network = ipaddress.ip_network(entry.cidr, strict=False)
            if addr in network:
                return True
        return False

    def remove(self, installation_id: str, entry_id: str) -> bool:
        key = (installation_id, entry_id)
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def list_entries(self, installation_id: str, include_expired: bool = False) -> list[AllowlistEntry]:
        entries = [e for (inst, _), e in self._entries.items() if inst == installation_id]
        if not include_expired:
            entries = [e for e in entries if not e.is_expired]
        return entries

    def count(self, installation_id: str) -> int:
        return len([e for (inst, _), e in self._entries.items() if inst == installation_id and not e.is_expired])
