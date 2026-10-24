"""Fleet Atlantis — track Terraform PR automation."""
from __future__ import annotations
def fleet_atlantis_status(repos: list[dict]) -> dict:
    enabled = [r for r in repos if r.get("atlantis_enabled", False)]
    plans_24h = sum(r.get("plans_24h", 0) for r in enabled)
    applies_24h = sum(r.get("applies_24h", 0) for r in enabled)
    return {"total": len(repos), "enabled": len(enabled), "plans_24h": plans_24h,
            "applies_24h": applies_24h, "active": plans_24h > 0}
