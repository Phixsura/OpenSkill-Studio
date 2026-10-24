"""Fleet Dependabot — track dependency security updates."""
from __future__ import annotations
def fleet_dependabot_status(repos: list[dict]) -> dict:
    enabled = [r for r in repos if r.get("dependabot_enabled", False)]
    security_alerts = sum(r.get("security_alerts", 0) for r in repos)
    auto_merged = sum(r.get("auto_merged_30d", 0) for r in enabled)
    return {"total": len(repos), "enabled": len(enabled), "security_alerts": security_alerts,
            "auto_merged_30d": auto_merged, "secure": security_alerts == 0}
