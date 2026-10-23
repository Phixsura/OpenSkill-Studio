"""Canary deployment controller — gradual rollout with health checks."""
from __future__ import annotations


class CanaryController:
    def __init__(self):
        self._deployments: dict[str, dict] = {}

    def start_canary(self, *, app_id: str, version: str, target_pct: int = 10,
                      step_pct: int = 10, health_threshold: float = 0.99) -> dict:
        self._deployments[app_id] = {
            "version": version, "current_pct": target_pct,
            "target_pct": target_pct, "step_pct": step_pct,
            "health_threshold": health_threshold,
            "phase": "canary", "checks": [],
        }
        return {"app_id": app_id, "version": version, "phase": "canary",
                "traffic_pct": target_pct}

    def check_health(self, app_id: str, *, success_rate: float, latency_p99: float) -> dict:
        d = self._deployments.get(app_id)
        if not d:
            return {"error": "No active canary"}
        healthy = success_rate >= d["health_threshold"]
        d["checks"].append({"success_rate": success_rate, "latency_p99": latency_p99, "healthy": healthy})
        if not healthy:
            d["phase"] = "rollback"
            d["current_pct"] = 0
            return {"action": "rollback", "reason": f"Success rate {success_rate} below {d['health_threshold']}",
                    "app_id": app_id}
        new_pct = min(d["current_pct"] + d["step_pct"], 100)
        d["current_pct"] = new_pct
        if new_pct >= 100:
            d["phase"] = "promoted"
        return {"action": "promote" if new_pct >= 100 else "advance",
                "traffic_pct": new_pct, "app_id": app_id, "phase": d["phase"]}

    def status(self, app_id: str) -> dict:
        d = self._deployments.get(app_id)
        if not d:
            return {"error": "Not found"}
        return {"app_id": app_id, "version": d["version"], "phase": d["phase"],
                "traffic_pct": d["current_pct"], "checks_count": len(d["checks"])}
