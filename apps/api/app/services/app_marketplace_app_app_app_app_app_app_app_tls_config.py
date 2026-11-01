"""SSL/TLS configuration manager — manage TLS settings and ciphers."""
from __future__ import annotations

TLS_VERSIONS = {"1.0": "deprecated", "1.1": "deprecated", "1.2": "supported", "1.3": "recommended"}

CIPHER_SUITES = {
    "strong": ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"],
    "moderate": ["TLS_AES_128_GCM_SHA256"],
    "weak": ["TLS_RSA_WITH_AES_128_CBC_SHA"],
}


def evaluate_tls_config(min_version: str, ciphers: list[str]) -> dict:
    version_status = TLS_VERSIONS.get(min_version, "unknown")
    weak_ciphers = [c for c in ciphers if c in CIPHER_SUITES.get("weak", [])]
    grade = "A" if min_version == "1.3" and not weak_ciphers else \
            "B" if min_version == "1.2" and not weak_ciphers else \
            "C" if min_version == "1.2" else "F"
    return {"min_version": min_version, "version_status": version_status,
            "cipher_count": len(ciphers), "weak_ciphers": weak_ciphers,
            "grade": grade, "secure": grade in ("A", "B")}


def tls_summary(configs: list[dict]) -> dict:
    secure = sum(1 for c in configs if c.get("secure"))
    return {"total": len(configs), "secure": secure, "insecure": len(configs) - secure,
            "secure_pct": round(secure / max(len(configs), 1) * 100)}
