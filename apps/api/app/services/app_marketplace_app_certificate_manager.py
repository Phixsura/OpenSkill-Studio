"""Certificate manager — manage TLS/SSL certificates for custom domains."""

import secrets
from datetime import datetime, timedelta


def issue_certificate(*, domain: str, cert_type: str = "auto") -> dict:
    valid_types = {"auto", "custom", "wildcard"}
    if cert_type not in valid_types:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(valid_types))}"}
    now = datetime.utcnow()
    return {
        "cert_id": f"cert_{secrets.token_urlsafe(8)}",
        "domain": domain,
        "type": cert_type,
        "issuer": "Let's Encrypt" if cert_type == "auto" else "Custom CA",
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(days=90 if cert_type == "auto" else 365)).isoformat(),
        "status": "active",
        "auto_renew": cert_type == "auto",
    }


def check_certificate_health(*, certificates: list[dict]) -> dict:
    now = datetime.utcnow()
    results = []
    for cert in certificates:
        expires = datetime.fromisoformat(cert["expires_at"])
        days_left = (expires - now).days
        results.append({
            "domain": cert["domain"],
            "days_until_expiry": days_left,
            "status": "valid" if days_left > 30 else "expiring" if days_left > 0 else "expired",
            "auto_renew": cert.get("auto_renew", False),
        })
    expiring = sum(1 for r in results if r["status"] != "valid")
    return {"certificates": results, "total": len(results),
            "expiring_count": expiring, "all_valid": expiring == 0}
