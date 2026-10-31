"""Fleet Blue-Green v9 — track blue-green deployment switches."""
from __future__ import annotations
def fleet_blue_green_v9(deployments: list[dict]) -> dict:
    blue = [d for d in deployments if d.get("env") == "blue"]
    green = [d for d in deployments if d.get("env") == "green"]
    active_env = "blue" if any(d.get("active") for d in blue) else "green"
    return {"total": len(deployments), "blue": len(blue), "green": len(green),
            "active_env": active_env, "healthy": True}
