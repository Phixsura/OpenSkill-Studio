"""Custom domain manager — validate, configure, and verify custom domains."""
from __future__ import annotations
import re
from urllib.parse import urlparse

DOMAIN_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$")


def validate_domain(domain: str) -> dict:
    domain = domain.strip().lower()
    if not DOMAIN_RE.match(domain):
        return {"valid": False, "domain": domain, "error": "Invalid domain format"}
    parts = domain.split(".")
    tld = parts[-1]
    return {"valid": True, "domain": domain, "tld": tld, "subdomain": parts[0] if len(parts) > 2 else None}


def configure_domain(domain: str, *, target: str = "app.openskill.io",
                      ssl: bool = True) -> dict:
    v = validate_domain(domain)
    if not v["valid"]:
        return v
    dns_records = [
        {"type": "CNAME", "name": domain, "value": target, "ttl": 3600},
    ]
    if ssl:
        dns_records.append({"type": "TXT", "name": f"_acme-challenge.{domain}",
                             "value": "pending_verification", "ttl": 300})
    return {
        "domain": domain, "target": target, "ssl": ssl,
        "status": "pending_verification",
        "dns_records": dns_records,
        "verification_token": f"openskill-verify-{domain.replace('.', '-')}",
    }


def verify_domain(domain: str, *, txt_records: list[str] | None = None) -> dict:
    v = validate_domain(domain)
    if not v["valid"]:
        return v
    token = f"openskill-verify-{domain.replace('.', '-')}"
    verified = txt_records is not None and token in txt_records
    return {"domain": domain, "verified": verified,
            "status": "active" if verified else "pending",
            "token_expected": token}
