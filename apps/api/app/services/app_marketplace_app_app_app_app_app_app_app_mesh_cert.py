"""Service mesh certificate manager — manage mTLS certificates between services."""
from __future__ import annotations
import secrets, hashlib


class MeshCertManager:
    def __init__(self):
        self._certs: dict[str, dict] = {}

    def issue(self, service: str, validity_days: int = 365) -> dict:
        serial = secrets.token_hex(8)
        fingerprint = hashlib.sha256(f"{service}:{serial}".encode()).hexdigest()[:20]
        self._certs[service] = {"service": service, "serial": serial,
                                 "fingerprint": fingerprint,
                                 "validity_days": validity_days, "status": "active"}
        return self._certs[service]

    def rotate(self, service: str) -> dict:
        old = self._certs.get(service, {}).get("fingerprint", "")
        new_cert = self.issue(service)
        return {"service": service, "old_fingerprint": old,
                "new_fingerprint": new_cert["fingerprint"], "rotated": True}

    def revoke(self, service: str) -> dict:
        if service in self._certs:
            self._certs[service]["status"] = "revoked"
            return {"service": service, "revoked": True}
        return {"service": service, "revoked": False}

    def verify(self, service: str) -> dict:
        cert = self._certs.get(service)
        if not cert:
            return {"service": service, "valid": False, "reason": "no_cert"}
        return {"service": service, "valid": cert["status"] == "active",
                "fingerprint": cert["fingerprint"]}

    def stats(self) -> dict:
        active = sum(1 for c in self._certs.values() if c["status"] == "active")
        return {"total": len(self._certs), "active": active,
                "revoked": len(self._certs) - active}
