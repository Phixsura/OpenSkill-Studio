"""Developer verification — verify developer account ownership."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

_verification_codes: dict[str, dict] = {}


def create_verification_code(*, developer_id: str, email: str) -> str:
    """Create a verification code for email verification."""
    code = secrets.token_urlsafe(32)
    _verification_codes[code] = {
        "developer_id": developer_id,
        "email": email,
        "created_at": datetime.now(UTC).isoformat(),
        "expires_at": (datetime.now(UTC) + timedelta(hours=24)).isoformat(),
        "used": False,
    }
    return code


def verify_code(code: str) -> dict | None:
    """Verify a code. Returns developer info or None."""
    entry = _verification_codes.get(code)
    if not entry or entry["used"]:
        return None
    if datetime.fromisoformat(entry["expires_at"]) < datetime.now(UTC):
        _verification_codes.pop(code, None)
        return None
    entry["used"] = True
    return {"developer_id": entry["developer_id"], "email": entry["email"], "verified": True}


def generate_domain_challenge(domain: str) -> dict:
    """Generate a DNS TXT record challenge for domain verification."""
    token = hashlib.sha256(f"{domain}:{secrets.token_hex(16)}".encode()).hexdigest()[:32]
    return {"type": "dns_txt", "domain": domain, "record_name": "_openskill-verify", "record_value": token}
