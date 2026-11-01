"""Fleet dependency update policy — track auto-update adoption."""
from __future__ import annotations
def fleet_dep_update_policy(repos: list[dict]) -> dict:
    auto_update = [r for r in repos if r.get("auto_update", False)]
    pinned = [r for r in repos if r.get("version_pinned", False)]
    return {"total": len(repos), "auto_update": len(auto_update),
            "pinned": len(pinned), "modern": len(auto_update) == len(repos)}
