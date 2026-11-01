"""Fleet mTLS — track mutual TLS adoption across mesh."""
from __future__ import annotations
def fleet_mtls_status(services: list[dict]) -> dict:
    enabled = [s for s in services if s.get("mtls_enabled", False)]
    pct = round(len(enabled) / max(len(services), 1) * 100, 1)
    return {"total": len(services), "mtls_enabled": len(enabled), "pct": pct, "full_coverage": pct == 100}
