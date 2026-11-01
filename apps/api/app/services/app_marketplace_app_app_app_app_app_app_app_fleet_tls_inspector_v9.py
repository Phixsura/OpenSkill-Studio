"""Fleet TLS Inspector v9 — track TLS certificate chain and cipher suites."""
from __future__ import annotations
def fleet_tls_inspector_v9(endpoints: list[dict]) -> dict:
    tls13 = [e for e in endpoints if e.get("tls_version") == "1.3"]
    weak_cipher = [e for e in endpoints if e.get("weak_cipher")]
    expiring = [e for e in endpoints if e.get("days_to_expiry", 999) < 30]
    return {"endpoints": len(endpoints), "tls_1_3": len(tls13), "weak_ciphers": len(weak_cipher),
            "expiring_soon": len(expiring), "healthy": len(weak_cipher) == 0 and len(expiring) == 0}
