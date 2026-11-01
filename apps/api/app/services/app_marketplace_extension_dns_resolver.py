"""DNS Resolver — manage custom domain mappings for extension endpoints.

Allows extensions to register custom subdomains and verify domain
ownership for branded extension URLs.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DomainMapping:
    domain: str
    extension_id: str
    org_id: str
    status: str = "pending"  # pending, verified, active, failed
    verification_token: str = ""
    verified_at: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.verification_token:
            raw = f"{self.domain}:{self.extension_id}:{self.created_at}"
            self.verification_token = f"osk-verify-{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


class DNSResolverService:
    """Manages custom domain mappings for extensions."""

    RESERVED_SUBDOMAINS = {"www", "api", "admin", "app", "docs", "status", "mail"}

    def __init__(self, base_domain: str = "ext.openskill.dev"):
        self._mappings: dict[str, DomainMapping] = {}
        self._base_domain = base_domain

    def register_subdomain(self, subdomain: str, extension_id: str,
                           org_id: str) -> tuple[DomainMapping | None, str]:
        """Register a subdomain under the platform domain."""
        if subdomain.lower() in self.RESERVED_SUBDOMAINS:
            return None, f"Subdomain '{subdomain}' is reserved"
        domain = f"{subdomain}.{self._base_domain}"
        if domain in self._mappings:
            return None, f"Domain '{domain}' already registered"
        mapping = DomainMapping(domain, extension_id, org_id, status="active")
        self._mappings[domain] = mapping
        return mapping, "Registered"

    def register_custom_domain(self, domain: str, extension_id: str,
                               org_id: str) -> tuple[DomainMapping, str]:
        """Register a custom domain — requires verification."""
        mapping = DomainMapping(domain, extension_id, org_id, status="pending")
        self._mappings[domain] = mapping
        return mapping, f"Add TXT record: {mapping.verification_token}"

    def verify_domain(self, domain: str, provided_token: str) -> tuple[bool, str]:
        """Verify domain ownership via TXT record token."""
        mapping = self._mappings.get(domain)
        if not mapping:
            return False, "Domain not registered"
        if mapping.status != "pending":
            return False, f"Domain is already {mapping.status}"
        if provided_token != mapping.verification_token:
            return False, "Verification token mismatch"
        mapping.status = "verified"
        mapping.verified_at = datetime.now(timezone.utc).isoformat()
        return True, "Domain verified"

    def activate(self, domain: str) -> bool:
        mapping = self._mappings.get(domain)
        if mapping and mapping.status == "verified":
            mapping.status = "active"
            return True
        return False

    def resolve(self, domain: str) -> DomainMapping | None:
        mapping = self._mappings.get(domain)
        if mapping and mapping.status == "active":
            return mapping
        return None

    def list_domains(self, extension_id: str) -> list[DomainMapping]:
        return [m for m in self._mappings.values() if m.extension_id == extension_id]

    def remove_domain(self, domain: str) -> bool:
        return self._mappings.pop(domain, None) is not None
