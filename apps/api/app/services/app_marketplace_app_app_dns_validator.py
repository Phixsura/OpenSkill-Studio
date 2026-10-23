"""DNS validator — custom domain verification and DNS record checker."""

import re
import html
import hashlib
import secrets

DOMAIN_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$")


def validate_domain(*, domain: str) -> dict:
    d = domain.strip().lower()
    if not DOMAIN_RE.match(d):
        return {"valid": False, "domain": d, "error": "Invalid domain format"}
    parts = d.split(".")
    return {"valid": True, "domain": d, "tld": parts[-1],
            "subdomain": ".".join(parts[:-2]) if len(parts) > 2 else None,
            "root": ".".join(parts[-2:])}


def generate_verification_record(*, domain: str, app_id: str) -> dict:
    token = hashlib.sha256(f"{domain}:{app_id}:{secrets.token_hex(8)}".encode()).hexdigest()[:32]
    return {
        "type": "TXT",
        "name": f"_openskill-verify.{domain}",
        "value": f"openskill-verify={token}",
        "token": token,
        "instructions": f"Add a TXT record to {html.escape(domain)} DNS settings",
    }
