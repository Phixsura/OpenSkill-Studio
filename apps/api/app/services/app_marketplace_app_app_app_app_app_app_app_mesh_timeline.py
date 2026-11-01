"""Mesh health timeline — track mesh health over time."""
from __future__ import annotations


def build_timeline(snapshots: list[dict]) -> dict:
    entries = []
    for s in snapshots:
        healthy = s.get("healthy", 0)
        total = s.get("total", 0)
        pct = round(healthy / max(total, 1) * 100, 1)
        entries.append({"timestamp": s.get("timestamp", 0), "healthy": healthy,
                        "total": total, "health_pct": pct,
                        "status": "healthy" if pct >= 100 else ("degraded" if pct >= 50 else "critical")})
    if len(entries) >= 2:
        trend = "improving" if entries[-1]["health_pct"] > entries[0]["health_pct"] + 1 else (
            "declining" if entries[-1]["health_pct"] < entries[0]["health_pct"] - 1 else "stable")
    else:
        trend = "stable"
    return {"entries": entries, "data_points": len(entries), "trend": trend,
            "current_pct": entries[-1]["health_pct"] if entries else 100}
