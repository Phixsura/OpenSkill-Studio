"""API Consumer Mutual TLS — manage mTLS certificates for API authentication."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
import structlog

log = structlog.get_logger()

class CertStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class MtlsCert:
    cert_id: str
    consumer_id: str
    fingerprint: str  # SHA-256 of cert
    subject_cn: str
    status: CertStatus = CertStatus.ACTIVE
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTls:
    def __init__(self) -> None:
        self._certs: dict[tuple[str, str], MtlsCert] = {}

    def register_cert(self, installation_id: str, cert: MtlsCert) -> MtlsCert:
        if not installation_id: raise ValueError("installation_id is required")
        if not cert.fingerprint or len(cert.fingerprint) < 16: raise ValueError("Valid certificate fingerprint required")
        # Check fingerprint uniqueness
        for (inst, _), existing in self._certs.items():
            if inst == installation_id and existing.fingerprint == cert.fingerprint and existing.status == CertStatus.ACTIVE:
                raise ValueError("Certificate fingerprint already registered")
        key = (installation_id, cert.cert_id)
        if key in self._certs: raise ValueError(f"cert_id {cert.cert_id} already exists")
        self._certs[key] = cert
        return cert

    def verify(self, installation_id: str, fingerprint: str) -> MtlsCert | None:
        now = time.time()
        for (inst, _), cert in self._certs.items():
            if inst == installation_id and cert.fingerprint == fingerprint:
                if cert.status == CertStatus.REVOKED: return None
                if cert.expires_at > 0 and cert.expires_at < now:
                    cert.status = CertStatus.EXPIRED
                    return None
                return cert
        return None

    def revoke(self, installation_id: str, cert_id: str) -> MtlsCert:
        cert = self._get(installation_id, cert_id)
        cert.status = CertStatus.REVOKED
        return cert

    def list_certs(self, installation_id: str, consumer_id: str | None = None) -> list[MtlsCert]:
        certs = [c for (inst, _), c in self._certs.items() if inst == installation_id]
        if consumer_id: certs = [c for c in certs if c.consumer_id == consumer_id]
        return certs

    def _get(self, installation_id: str, cert_id: str) -> MtlsCert:
        c = self._certs.get((installation_id, cert_id))
        if c is None: raise KeyError(f"Cert {cert_id} not found")
        return c
