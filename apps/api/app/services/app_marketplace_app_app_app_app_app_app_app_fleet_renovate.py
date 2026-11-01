"""Fleet Renovate — track dependency update automation."""
from __future__ import annotations
def fleet_renovate_status(repos: list[dict]) -> dict:
    enabled = [r for r in repos if r.get("renovate_enabled", False)]
    prs_open = sum(r.get("open_prs", 0) for r in enabled)
    prs_merged = sum(r.get("merged_prs_30d", 0) for r in enabled)
    return {"total": len(repos), "enabled": len(enabled), "open_prs": prs_open,
            "merged_30d": prs_merged, "active": prs_merged > 0}
