"""Custom domain — manage custom domains for developer apps."""

import re

DOMAIN_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.[a-z]{2,})+$")


def validate_domain(*, domain: str) -> dict:
    d = domain.lower().strip()
    if not DOMAIN_RE.match(d):
        return {"valid": False, "error": "Invalid domain format"}
    if d.endswith((".openskill.dev", ".openskill.com")):
        return {"valid": False, "error": "Cannot use openskill subdomains"}
    return {"valid": True, "domain": d}


def setup_custom_domain(*, app_id: str, domain: str) -> dict:
    v = validate_domain(domain=domain)
    if not v["valid"]:
        return {"success": False, "error": v["error"]}
    return {
        "success": True,
        "app_id": app_id,
        "domain": v["domain"],
        "dns_records": [
            {"type": "CNAME", "name": v["domain"], "value": "apps.openskill.dev"},
            {"type": "TXT", "name": f"_verify.{v['domain']}", "value": f"openskill-verify={app_id}"},
        ],
        "ssl_status": "pending",
        "verification_status": "pending",
    }


def check_domain_status(*, domain: str) -> dict:
    return {"domain": domain, "dns_configured": True,
            "ssl_status": "active", "verification_status": "verified",
            "expires_at": "2027-10-23T00:00:00"}
