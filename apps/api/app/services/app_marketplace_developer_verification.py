"""Developer verification — identity and domain verification flow."""

import hashlib
import re
from datetime import datetime, timezone

DOMAIN_TXT_PREFIX = "openskill-verify="


def initiate_domain_verification(*, developer_id: str, domain: str) -> dict:
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*\.)+[a-zA-Z]{2,}$', domain):
        return {"error": "Invalid domain format"}
    token = hashlib.sha256(f"{developer_id}:{domain}".encode()).hexdigest()[:32]
    return {
        "developer_id": developer_id, "domain": domain,
        "verification_token": token,
        "txt_record": f"{DOMAIN_TXT_PREFIX}{token}",
        "status": "pending", "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def check_verification(*, expected_token: str, found_records: list[str]) -> dict:
    target = f"{DOMAIN_TXT_PREFIX}{expected_token}"
    verified = target in found_records
    return {"verified": verified, "checked_at": datetime.now(timezone.utc).isoformat()}


def get_verification_badge(*, verified_domain: bool, verified_email: bool,
                              published_apps: int) -> dict:
    level = "none"
    if verified_email:
        level = "basic"
    if verified_domain:
        level = "verified"
    if verified_domain and published_apps >= 3:
        level = "trusted"
    return {"level": level, "verified_domain": verified_domain,
            "verified_email": verified_email, "published_apps": published_apps}
