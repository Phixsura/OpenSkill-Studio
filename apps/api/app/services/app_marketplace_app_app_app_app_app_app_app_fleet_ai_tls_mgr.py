"""Fleet AI TLS Manager — track AI service TLS certificate management."""
from __future__ import annotations
def fleet_ai_tls_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    certs = sum(m.get("certs", 0) for m in managers)
    expiring_30d = sum(m.get("expiring_30d", 0) for m in managers)
    auto_renewed = sum(m.get("auto_renewed", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "certs": certs,
            "expiring_30d": expiring_30d, "auto_renewed": auto_renewed, "healthy": expiring_30d == 0}
