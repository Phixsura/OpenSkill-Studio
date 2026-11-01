"""Fleet Ingress Controller v9 — track ingress routing and TLS termination."""
from __future__ import annotations
def fleet_ingress_ctrl_v9(rules: list[dict]) -> dict:
    active = [r for r in rules if r.get("active", True)]
    tls = [r for r in rules if r.get("tls_enabled")]
    rps = sum(r.get("rps", 0) for r in rules)
    return {"rules": len(rules), "active": len(active), "tls_enabled": len(tls),
            "total_rps": rps, "healthy": len(tls) == len(rules)}
