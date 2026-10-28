"""App Custom Domain Manager — manage custom domains for installed apps.

Handles custom domain lifecycle:
- Register domains with DNS verification
- Track verification status
- SSL certificate status tracking
- Per-installation scoped domains
"""

from __future__ import annotations

import re
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()

_DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$")


class DomainStatus(str, Enum):
    PENDING = "pending"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    FAILED = "failed"


class SSLStatus(str, Enum):
    NONE = "none"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    EXPIRED = "expired"


@dataclass
class CustomDomain:
    """A custom domain record."""

    domain_id: str
    installation_id: str
    domain: str
    status: DomainStatus = DomainStatus.PENDING
    ssl_status: SSLStatus = SSLStatus.NONE
    verification_token: str = ""
    created_at: float = field(default_factory=time.time)
    verified_at: float | None = None


class AppCustomDomainManager:
    """Manage custom domains for installed apps."""

    def __init__(self) -> None:
        self._domains: dict[tuple[str, str], CustomDomain] = {}

    def register_domain(
        self,
        installation_id: str,
        domain_id: str,
        domain: str,
        now: float | None = None,
    ) -> CustomDomain:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not domain_id:
            raise ValueError("domain_id is required")
        if not _DOMAIN_RE.match(domain.lower()):
            raise ValueError(f"Invalid domain: {domain}")

        key = (installation_id, domain_id)
        if key in self._domains:
            raise ValueError(f"Domain {domain_id} already exists")

        # Check domain uniqueness across all installations
        for (_, _), d in self._domains.items():
            if d.domain.lower() == domain.lower():
                raise ValueError(f"Domain {domain} already registered")

        token = f"openskill-verify-{secrets.token_urlsafe(32)}"
        record = CustomDomain(
            domain_id=domain_id, installation_id=installation_id,
            domain=domain.lower(), verification_token=token,
            created_at=now or time.time(),
        )
        self._domains[key] = record
        return record

    def start_verification(self, installation_id: str, domain_id: str) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        if d.status != DomainStatus.PENDING:
            raise ValueError(f"Cannot verify domain in {d.status} state")
        d.status = DomainStatus.VERIFYING
        return d

    def complete_verification(self, installation_id: str, domain_id: str, now: float | None = None) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        if d.status != DomainStatus.VERIFYING:
            raise ValueError(f"Cannot complete verification in {d.status} state")
        d.status = DomainStatus.VERIFIED
        d.verified_at = now or time.time()
        return d

    def fail_verification(self, installation_id: str, domain_id: str) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        d.status = DomainStatus.FAILED
        return d

    def update_ssl(self, installation_id: str, domain_id: str, ssl_status: SSLStatus) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        d.ssl_status = ssl_status
        return d

    def remove_domain(self, installation_id: str, domain_id: str) -> bool:
        key = (installation_id, domain_id)
        if key in self._domains:
            del self._domains[key]
            return True
        return False

    def get_domain(self, installation_id: str, domain_id: str) -> CustomDomain:
        return self._get(installation_id, domain_id)

    def list_domains(self, installation_id: str) -> list[CustomDomain]:
        return [d for (inst, _), d in self._domains.items() if inst == installation_id]

    def _get(self, installation_id: str, domain_id: str) -> CustomDomain:
        key = (installation_id, domain_id)
        d = self._domains.get(key)
        if d is None:
            raise KeyError(f"Domain {domain_id} not found")
        return d
