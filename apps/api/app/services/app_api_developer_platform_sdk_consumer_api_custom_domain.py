"""Consumer Custom Domain — custom domain mapping with SSL status."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

DOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")


@dataclass
class CustomDomain:
    domain: str
    consumer_id: str
    ssl_status: str = "pending"  # pending, provisioning, active, failed, expired
    dns_verified: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ssl_expires_at: str = ""
    cname_target: str = ""


@dataclass
class CustomDomainManager:
    """Manage custom domain mappings with DNS verification and SSL."""

    _domains: dict[str, CustomDomain] = field(default_factory=dict)

    def add_domain(self, consumer_id: str, domain: str) -> dict:
        if not DOMAIN_RE.match(domain.lower()):
            raise ValueError(f"Invalid domain: {domain}")
        if domain in self._domains:
            raise ValueError(f"Domain {domain} already registered")
        cname = f"{consumer_id}.api.platform.io"
        self._domains[domain] = CustomDomain(
            domain=domain, consumer_id=consumer_id, cname_target=cname,
        )
        logger.info("domain_added", domain=domain, consumer_id=consumer_id)
        return {"domain": domain, "cname_target": cname,
                "dns_record": f"CNAME {domain} -> {cname}"}

    def verify_dns(self, domain: str, verified: bool = True) -> dict:
        d = self._domains.get(domain)
        if not d:
            raise ValueError(f"Domain {domain} not found")
        d.dns_verified = verified
        if verified:
            d.ssl_status = "provisioning"
        return {"domain": domain, "dns_verified": verified, "ssl_status": d.ssl_status}

    def provision_ssl(self, domain: str, success: bool = True,
                      expires_at: str = "") -> dict:
        d = self._domains.get(domain)
        if not d:
            raise ValueError(f"Domain {domain} not found")
        if not d.dns_verified:
            return {"error": "dns_not_verified"}
        if success:
            d.ssl_status = "active"
            d.ssl_expires_at = expires_at
        else:
            d.ssl_status = "failed"
        return {"domain": domain, "ssl_status": d.ssl_status}

    def remove_domain(self, domain: str) -> dict:
        if domain in self._domains:
            del self._domains[domain]
            return {"removed": True}
        return {"removed": False}

    def get_domain(self, domain: str) -> dict | None:
        d = self._domains.get(domain)
        if not d:
            return None
        return {
            "domain": d.domain, "consumer_id": d.consumer_id,
            "ssl_status": d.ssl_status, "dns_verified": d.dns_verified,
            "cname_target": d.cname_target, "ssl_expires_at": d.ssl_expires_at,
        }

    def list_domains(self, consumer_id: str | None = None) -> list[dict]:
        domains = list(self._domains.values())
        if consumer_id:
            domains = [d for d in domains if d.consumer_id == consumer_id]
        return [self.get_domain(d.domain) for d in domains]

    def check_ssl_expiry(self, warn_days: int = 30) -> list[dict]:
        expiring = []
        for d in self._domains.values():
            if d.ssl_status == "active" and d.ssl_expires_at:
                expiring.append({
                    "domain": d.domain, "expires_at": d.ssl_expires_at,
                    "consumer_id": d.consumer_id,
                })
        return expiring

    def get_stats(self) -> dict:
        domains = list(self._domains.values())
        return {
            "total_domains": len(domains),
            "ssl_active": sum(1 for d in domains if d.ssl_status == "active"),
            "dns_verified": sum(1 for d in domains if d.dns_verified),
            "pending": sum(1 for d in domains if d.ssl_status == "pending"),
        }
