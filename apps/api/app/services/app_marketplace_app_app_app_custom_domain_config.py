"""Custom domain config — custom domain setup and SSL certificate management."""

import html
import re
from urllib.parse import urlparse

DOMAIN_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$")


def configure_custom_domain(*, domain: str, app_id: str) -> dict:
    d = domain.strip().lower()
    if not DOMAIN_RE.match(d):
        return {"error": "Invalid domain format"}
    return {
        "domain": d, "app_id": app_id,
        "status": "pending_verification",
        "dns_records": [
            {"type": "CNAME", "name": d, "value": f"{app_id}.apps.openskill.dev"},
            {"type": "TXT", "name": f"_openskill.{d}", "value": f"verify={app_id}"},
        ],
        "ssl": {"status": "pending", "issuer": "Let's Encrypt", "auto_renew": True},
    }


def check_domain_status(*, verified: bool, ssl_active: bool) -> dict:
    if verified and ssl_active:
        return {"status": "active", "icon": "🟢", "message": "Domain is active with SSL"}
    if verified:
        return {"status": "ssl_pending", "icon": "🟡", "message": "Verified, SSL provisioning..."}
    return {"status": "pending", "icon": "🔴", "message": "Waiting for DNS verification"}
