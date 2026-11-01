"""API gateway TLS terminator — manage TLS termination at the gateway."""
from __future__ import annotations
import hashlib


class TlsTerminator:
    def __init__(self):
        self._certs: dict[str, dict] = {}
        self._connections = 0
        self._handshakes = 0

    def add_cert(self, domain: str, cert_hash: str, expires_days: int) -> dict:
        self._certs[domain] = {"domain": domain, "cert_hash": cert_hash,
                                "expires_days": expires_days, "active": True}
        return self._certs[domain]

    def terminate(self, domain: str) -> dict:
        self._connections += 1
        self._handshakes += 1
        cert = self._certs.get(domain)
        if not cert or not cert["active"]:
            return {"terminated": False, "reason": "no_cert"}
        if cert["expires_days"] <= 0:
            return {"terminated": False, "reason": "cert_expired"}
        return {"terminated": True, "domain": domain, "protocol": "TLS 1.3"}

    def stats(self) -> dict:
        active = sum(1 for c in self._certs.values() if c["active"])
        expiring = sum(1 for c in self._certs.values() if 0 < c["expires_days"] <= 30)
        return {"domains": len(self._certs), "active": active, "expiring_soon": expiring,
                "total_connections": self._connections}
