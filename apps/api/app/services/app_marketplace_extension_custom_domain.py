"""Extension Custom Domain — map custom domains to extension pages."""
from __future__ import annotations
from dataclasses import dataclass
import re
import time

DOMAIN_RE = re.compile(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$')


@dataclass
class CustomDomain:
    domain: str
    extension_id: str
    verified: bool = False
    ssl_active: bool = False
    verification_token: str = ""
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtCustomDomainService:
    def __init__(self):
        self._domains: dict[str, CustomDomain] = {}  # domain -> entry

    def add(self, extension_id: str, domain: str) -> CustomDomain:
        domain = domain.lower().strip()
        if not DOMAIN_RE.match(domain):
            raise ValueError("Invalid domain format")
        if domain in self._domains:
            raise ValueError("Domain already registered")
        import secrets
        cd = CustomDomain(domain=domain, extension_id=extension_id,
                          verification_token=secrets.token_urlsafe(32))
        self._domains[domain] = cd
        return cd

    def verify(self, domain: str, token: str) -> bool:
        cd = self._domains.get(domain)
        if not cd or cd.verified:
            return False
        if cd.verification_token == token:
            cd.verified = True
            cd.ssl_active = True
            return True
        return False

    def remove(self, domain: str, extension_id: str) -> bool:
        cd = self._domains.get(domain)
        if cd and cd.extension_id == extension_id:
            del self._domains[domain]
            return True
        return False

    def get_by_extension(self, extension_id: str) -> list[CustomDomain]:
        return [d for d in self._domains.values() if d.extension_id == extension_id]

    def resolve(self, domain: str) -> str | None:
        cd = self._domains.get(domain)
        if cd and cd.verified:
            return cd.extension_id
        return None
