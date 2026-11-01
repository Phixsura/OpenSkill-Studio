"""Fleet Release Train v9 — track release cadence and version management."""
from __future__ import annotations
def fleet_release_train_v9(releases: list[dict]) -> dict:
    shipped = [r for r in releases if r.get("shipped")]
    hotfixes = [r for r in releases if r.get("type") == "hotfix"]
    avg_lead = sum(r.get("lead_time_hours", 0) for r in releases) / len(releases) if releases else 0
    return {"total": len(releases), "shipped": len(shipped), "hotfixes": len(hotfixes),
            "avg_lead_time_hours": round(avg_lead, 1), "healthy": avg_lead < 24}
