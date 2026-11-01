"""Consumer API Mutual TLS — manage client certificate authentication."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class ClientCertificate:
    cert_id: str
    consumer_id: str
    subject_cn: str
    fingerprint_sha256: str
    issuer: str = ""
    not_before: datetime | None = None
    not_after: datetime | None = None
    revoked: bool = False

@dataclass
class MTLSConfig:
    consumer_id: str
    required: bool = True
    allowed_issuers: list[str] = field(default_factory=list)

@dataclass
class VerifyResult:
    valid: bool
    consumer_id: str | None = None
    cert_id: str | None = None
    reason: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], MTLSConfig] = {}
        self._certs: dict[tuple[str, str], ClientCertificate] = {}  # (inst, fingerprint)

    def configure(self, installation_id: str, config: MTLSConfig) -> MTLSConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def register_cert(self, installation_id: str, cert: ClientCertificate) -> ClientCertificate:
        if not installation_id:
            raise ValueError("installation_id is required")
        if len(cert.fingerprint_sha256) != 64:
            raise ValueError("fingerprint must be 64-char SHA-256 hex")
        key = (installation_id, cert.fingerprint_sha256)
        self._certs[key] = cert
        log.info("cert_registered", installation_id=installation_id, consumer=cert.consumer_id, cn=cert.subject_cn)
        return cert

    def verify(self, installation_id: str, fingerprint: str, now: datetime) -> VerifyResult:
        key = (installation_id, fingerprint)
        cert = self._certs.get(key)
        if not cert:
            return VerifyResult(valid=False, reason="cert_not_found")
        if cert.revoked:
            return VerifyResult(valid=False, consumer_id=cert.consumer_id, cert_id=cert.cert_id, reason="cert_revoked")
        if cert.not_after and now > cert.not_after:
            return VerifyResult(valid=False, consumer_id=cert.consumer_id, cert_id=cert.cert_id, reason="cert_expired")
        if cert.not_before and now < cert.not_before:
            return VerifyResult(valid=False, consumer_id=cert.consumer_id, cert_id=cert.cert_id, reason="cert_not_yet_valid")
        # Check issuer allowlist
        config = self._configs.get((installation_id, cert.consumer_id))
        if config and config.allowed_issuers and cert.issuer not in config.allowed_issuers:
            return VerifyResult(valid=False, consumer_id=cert.consumer_id, cert_id=cert.cert_id, reason="issuer_not_allowed")
        return VerifyResult(valid=True, consumer_id=cert.consumer_id, cert_id=cert.cert_id, reason="valid")

    def revoke_cert(self, installation_id: str, fingerprint: str) -> ClientCertificate:
        key = (installation_id, fingerprint)
        cert = self._certs.get(key)
        if not cert:
            raise ValueError("Certificate not found")
        cert.revoked = True
        return cert

    def list_certs(self, installation_id: str, consumer_id: str) -> list[ClientCertificate]:
        return [c for (inst, _), c in self._certs.items() if inst == installation_id and c.consumer_id == consumer_id]
