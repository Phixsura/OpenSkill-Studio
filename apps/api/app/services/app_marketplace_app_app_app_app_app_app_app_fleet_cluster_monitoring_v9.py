"""Fleet Cluster Monitoring v9 — track cluster-wide monitoring health."""
from __future__ import annotations
def fleet_cluster_monitoring_v9(clusters: list[dict]) -> dict:
    monitored = [c for c in clusters if c.get("monitoring_enabled")]
    alerts_active = sum(c.get("active_alerts", 0) for c in clusters)
    dashboards = sum(c.get("dashboards", 0) for c in clusters)
    return {"clusters": len(clusters), "monitored": len(monitored), "active_alerts": alerts_active,
            "dashboards": dashboards, "healthy": alerts_active == 0}
