"""Fleet chaos monkey — automated failure injection status."""
from __future__ import annotations
def fleet_chaos_monkey(config: dict) -> dict:
    enabled = config.get("enabled", False)
    terminated = config.get("pods_terminated_24h", 0)
    survived = config.get("survived", 0)
    return {"enabled": enabled, "terminated_24h": terminated, "survived": survived,
            "survival_rate": round(survived / max(terminated, 1) * 100, 1)}
