"""API Consumer Custom Domain — manage custom domains for API access."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import re
import structlog

log = structlog.get_logger()

class DomainStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    ACTIVE = "active"
    FAILED = "failed"

@dataclass
class CustomDomain:
    domain_id: str
    consumer_id: str
    domain: str
    status: DomainStatus = DomainStatus.PENDING
    ssl_enabled: bool = True
    verification_token: str = ""

_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-.]+\.[a-zA-Z]{2,}$")

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomain:
    def __init__(self) -> None:
        self._domains: dict[tuple[str, str], CustomDomain] = {}

    def add_domain(self, installation_id: str, domain_entry: CustomDomain) -> CustomDomain:
        if not installation_id: raise ValueError("installation_id is required")
        if not _DOMAIN_RE.match(domain_entry.domain): raise ValueError(f"Invalid domain: {domain_entry.domain}")
        # Check uniqueness across all consumers
        for (inst, _), d in self._domains.items():
            if inst == installation_id and d.domain.lower() == domain_entry.domain.lower():
                raise ValueError(f"Domain {domain_entry.domain} already registered")
        key = (installation_id, domain_entry.domain_id)
        self._domains[key] = domain_entry
        return domain_entry

    def verify_domain(self, installation_id: str, domain_id: str) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        if d.status != DomainStatus.PENDING: raise ValueError(f"Domain is {d.status.value}")
        d.status = DomainStatus.VERIFIED
        return d

    def activate(self, installation_id: str, domain_id: str) -> CustomDomain:
        d = self._get(installation_id, domain_id)
        if d.status != DomainStatus.VERIFIED: raise ValueError("Domain must be verified first")
        d.status = DomainStatus.ACTIVE
        return d

    def list_domains(self, installation_id: str, consumer_id: str | None = None) -> list[CustomDomain]:
        domains = [d for (inst, _), d in self._domains.items() if inst == installation_id]
        if consumer_id: domains = [d for d in domains if d.consumer_id == consumer_id]
        return domains

    def _get(self, installation_id: str, domain_id: str) -> CustomDomain:
        d = self._domains.get((installation_id, domain_id))
        if d is None: raise KeyError(f"Domain {domain_id} not found")
        return d
