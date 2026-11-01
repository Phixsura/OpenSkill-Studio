"""App Custom Domain — manage custom domain mappings.

Manages custom domains for installed apps:
- Map custom domains to app endpoints
- SSL certificate status tracking
- DNS verification status
- Per-installation scoped domains
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class DomainStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class SSLStatus(str, Enum):
    NONE = "none"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    EXPIRED = "expired"


@dataclass
class CustomDomain:
    """A custom domain mapping."""

    domain_id: str
    hostname: str
    target: str  # app endpoint
    dns_status: DomainStatus = DomainStatus.PENDING
    ssl_status: SSLStatus = SSLStatus.NONE
    verification_token: str = ""
    created_at: float = field(default_factory=time.time)

    @property
    def is_ready(self) -> bool:
        return self.dns_status == DomainStatus.VERIFIED and self.ssl_status == SSLStatus.ACTIVE


class AppCustomDomain:
    """Manage custom domain mappings."""

    def __init__(self) -> None:
        self._domains: dict[tuple[str, str], CustomDomain] = {}

    def add_domain(
        self, installation_id: str, domain_id: str, hostname: str,
        target: str,
    ) -> CustomDomain:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not hostname:
            raise ValueError("hostname is required")
        if not target:
            raise ValueError("target is required")

        # Normalize hostname
        hostname = hostname.lower().strip().rstrip(".")

        # Cross-tenant uniqueness: reject hostname already registered by any installation
        if any(d.hostname == hostname for d in self._domains.values()):
            raise ValueError(f"Domain {hostname} already registered")

        key = (installation_id, domain_id)
        if key in self._domains:
            raise ValueError(f"Domain ID {domain_id} already exists")

        # Server-generated verification token
        verification_token = f"openskill-verify-{secrets.token_urlsafe(32)}"

        domain = CustomDomain(
            domain_id=domain_id, hostname=hostname, target=target,
            verification_token=verification_token,
        )
        self._domains[key] = domain
        return domain

    def verify_dns(self, installation_id: str, domain_id: str, success: bool) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        d.dns_status = DomainStatus.VERIFIED if success else DomainStatus.FAILED
        return d

    def update_ssl(self, installation_id: str, domain_id: str, status: SSLStatus) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        d.ssl_status = status
        return d

    def get_domain(self, installation_id: str, domain_id: str) -> CustomDomain:
        return self._get(installation_id, domain_id)

    def find_by_hostname(self, installation_id: str, hostname: str) -> CustomDomain | None:
        normalized = hostname.lower().strip().rstrip(".")
        for (inst, _), d in self._domains.items():
            if inst == installation_id and d.hostname == normalized:
                return d
        return None

    def ready_domains(self, installation_id: str) -> list[CustomDomain]:
        return [d for (inst, _), d in self._domains.items() if inst == installation_id and d.is_ready]

    def list_domains(self, installation_id: str) -> list[CustomDomain]:
        return [d for (inst, _), d in self._domains.items() if inst == installation_id]

    def remove(self, installation_id: str, domain_id: str) -> bool:
        key = (installation_id, domain_id)
        if key in self._domains:
            del self._domains[key]
            return True
        return False

    def _get(self, installation_id: str, domain_id: str) -> CustomDomain:
        key = (installation_id, domain_id)
        d = self._domains.get(key)
        if d is None:
            raise KeyError(f"Domain {domain_id} not found")
        return d
