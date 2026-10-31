"""Certificate manager — manage TLS certificates."""
from __future__ import annotations
import time
import hashlib


def create_cert(domain: str, issuer: str = "Let's Encrypt", validity_days: int = 90) -> dict:
    now = time.time()
    fingerprint = hashlib.sha256(f"{domain}:{now}".encode()).hexdigest()[:16]
    return {"domain": domain, "issuer": issuer, "fingerprint": fingerprint,
            "issued_at": now, "expires_at": now + validity_days * 86400,
            "validity_days": validity_days, "status": "active"}


def check_expiry(cert: dict, now: float | None = None) -> dict:
    now = now or time.time()
    days_left = round((cert["expires_at"] - now) / 86400, 1)
    if days_left <= 0:
        status = "expired"
    elif days_left <= 14:
        status = "expiring_soon"
    else:
        status = "valid"
    return {"domain": cert["domain"], "days_left": max(0, days_left),
            "status": status, "needs_renewal": days_left <= 30}


def summarize_certs(certs: list[dict]) -> dict:
    results = [check_expiry(c) for c in certs]
    expired = sum(1 for r in results if r["status"] == "expired")
    expiring = sum(1 for r in results if r["status"] == "expiring_soon")
    return {"total": len(certs), "valid": len(certs) - expired - expiring,
            "expiring_soon": expiring, "expired": expired,
            "needs_action": expired + expiring > 0}
