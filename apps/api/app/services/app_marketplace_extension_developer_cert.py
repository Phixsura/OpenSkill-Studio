"""Developer Certification — skill certification for extension developers.

Manages certification programs with exams, passing scores, certificate
issuance, expiry, and verification.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Certification:
    cert_id: str
    name: str
    description: str
    passing_score: int = 70
    questions: int = 50
    validity_days: int = 365


@dataclass
class CertResult:
    result_id: str
    developer_id: str
    cert_id: str
    score: int
    passed: bool
    issued_at: float = 0.0
    expires_at: float = 0.0
    certificate_code: str = ""


class DeveloperCertificationService:
    """Manages developer certification programs."""

    def __init__(self):
        self._certs: dict[str, Certification] = {}
        self._results: dict[str, list[CertResult]] = defaultdict(list)

    def create_cert(self, cert_id: str, name: str, description: str,
                    passing_score: int = 70, questions: int = 50,
                    validity_days: int = 365) -> Certification:
        cert = Certification(cert_id=cert_id, name=name, description=description,
                             passing_score=passing_score, questions=questions,
                             validity_days=validity_days)
        self._certs[cert_id] = cert
        return cert

    def submit_exam(self, developer_id: str, cert_id: str,
                    score: int) -> CertResult:
        cert = self._certs.get(cert_id)
        if not cert:
            raise ValueError("Certification not found")
        passed = score >= cert.passing_score
        now = time.time()
        result = CertResult(
            result_id=f"cr_{secrets.token_urlsafe(8)}",
            developer_id=developer_id, cert_id=cert_id,
            score=score, passed=passed,
            issued_at=now if passed else 0,
            expires_at=now + cert.validity_days * 86400 if passed else 0,
            certificate_code=f"CERT-{secrets.token_hex(6).upper()}" if passed else "",
        )
        self._results[developer_id].append(result)
        return result

    def verify(self, certificate_code: str) -> dict:
        for results in self._results.values():
            for r in results:
                if r.certificate_code == certificate_code:
                    expired = r.expires_at > 0 and time.time() > r.expires_at
                    cert = self._certs.get(r.cert_id)
                    return {
                        "valid": r.passed and not expired,
                        "developer_id": r.developer_id,
                        "certification": cert.name if cert else "",
                        "score": r.score, "expired": expired,
                    }
        return {"valid": False, "reason": "Certificate not found"}

    def get_developer_certs(self, developer_id: str) -> list[CertResult]:
        return [r for r in self._results.get(developer_id, []) if r.passed]

    def list_certs(self) -> list[Certification]:
        return list(self._certs.values())
