"""App API Developer Custom Domain Manager — manage custom domains for developer portals."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$")

@dataclass
class CustomDomain:
    domain: str
    status: str = "pending"  # "pending", "verified", "active", "failed"
    ssl_status: str = "pending"  # "pending", "provisioned", "failed"
    verification_token: str = ""

class AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager:
    def __init__(self) -> None:
        self._domains: dict[tuple[str, str], CustomDomain] = {}
        self._all_domains: set[str] = set()  # cross-tenant uniqueness

    def add(self, installation_id: str, domain: str, verification_token: str) -> CustomDomain:
        if not installation_id: raise ValueError("installation_id is required")
        if not _DOMAIN_RE.match(domain): raise ValueError(f"Invalid domain: {domain}")
        if domain in self._all_domains: raise ValueError(f"Domain {domain} already registered")
        key = (installation_id, domain)
        d = CustomDomain(domain=domain, verification_token=verification_token)
        self._domains[key] = d
        self._all_domains.add(domain)
        return d

    def verify(self, installation_id: str, domain: str) -> CustomDomain:
        d = self._get(installation_id, domain)
        d.status = "verified"
        return d

    def activate(self, installation_id: str, domain: str) -> CustomDomain:
        d = self._get(installation_id, domain)
        if d.status != "verified": raise ValueError("Domain must be verified first")
        d.status = "active"
        d.ssl_status = "provisioned"
        return d

    def active_domains(self, installation_id: str) -> list[CustomDomain]:
        return [d for (inst, _), d in self._domains.items() if inst == installation_id and d.status == "active"]

    def all_domains(self, installation_id: str) -> list[CustomDomain]:
        return [d for (inst, _), d in self._domains.items() if inst == installation_id]

    def _get(self, installation_id: str, domain: str) -> CustomDomain:
        key = (installation_id, domain)
        d = self._domains.get(key)
        if d is None: raise KeyError(f"Domain {domain} not found")
        return d
