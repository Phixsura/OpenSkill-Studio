"""Custom domain — manage custom domains for app landing pages."""

import re

DOMAIN_RE = re.compile(r'^([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')


def add_custom_domain(*, app_id: str, domain: str) -> dict:
    if not DOMAIN_RE.match(domain):
        return {"error": "Invalid domain format"}
    cname_target = f"{app_id}.apps.openskill.dev"
    return {
        "app_id": app_id, "domain": domain, "cname_target": cname_target,
        "status": "pending_verification", "ssl_status": "pending", "error": None,
    }


def verify_domain(*, domain_record: dict, cname_value: str) -> dict:
    expected = domain_record["cname_target"]
    verified = cname_value.rstrip(".") == expected or cname_value.rstrip(".") == expected + "."
    return {
        "domain": domain_record["domain"], "verified": verified,
        "status": "verified" if verified else "verification_failed",
    }


def remove_custom_domain(*, app_id: str, domain: str) -> dict:
    return {"app_id": app_id, "domain": domain, "status": "removed"}
