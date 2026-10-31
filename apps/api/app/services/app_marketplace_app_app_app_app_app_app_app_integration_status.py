"""Integration status — monitor health of third-party integrations."""
from __future__ import annotations


def check_integrations(integrations: list[dict]) -> dict:
    results = []
    connected = 0
    for intg in integrations:
        status = intg.get("status", "disconnected")
        last_sync = intg.get("last_sync", "never")
        if status == "connected":
            connected += 1
        results.append({
            "name": intg["name"], "provider": intg.get("provider", ""),
            "status": status, "last_sync": last_sync,
            "icon": intg.get("icon", "🔗"),
        })
    total = len(integrations)
    return {
        "total": total, "connected": connected,
        "disconnected": total - connected,
        "health": "all_connected" if connected == total else "partial" if connected > 0 else "none",
        "integrations": results,
    }
