"""Fleet API Security Posture v9 — comprehensive API security score."""
from __future__ import annotations
def fleet_api_security_posture_v9(apis: list[dict]) -> dict:
    secure = [a for a in apis if a.get("security_score", 0) > 90]
    auth_enforced = [a for a in apis if a.get("auth_enforced")]
    tls_only = [a for a in apis if a.get("tls_only")]
    avg_score = sum(a.get("security_score", 0) for a in apis) / len(apis) if apis else 0
    return {"apis": len(apis), "secure": len(secure), "auth_enforced": len(auth_enforced),
            "tls_only": len(tls_only), "avg_score": round(avg_score, 1), "healthy": avg_score > 90}
