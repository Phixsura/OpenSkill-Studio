"""Health check aggregator — collect and report health across all services."""
from __future__ import annotations


def aggregate_health(checks: list[dict]) -> dict:
    results = []
    healthy = 0
    for c in checks:
        status = c.get("status", "unknown")
        latency = c.get("latency_ms", 0)
        ok = status == "healthy"
        if ok:
            healthy += 1
        results.append({"name": c["name"], "status": status, "latency_ms": latency,
                         "message": c.get("message", "")})
    total = len(checks)
    pct = round(healthy / max(total, 1) * 100)
    overall = "healthy" if healthy == total else "degraded" if healthy > 0 else "down"
    return {
        "overall": overall, "healthy": healthy, "total": total,
        "health_pct": pct, "health_display": f"{pct}%",
        "checks": results,
        "issues": [r for r in results if r["status"] != "healthy"],
    }


def format_status_page(health: dict) -> dict:
    emoji = {"healthy": "🟢", "degraded": "🟡", "down": "🔴"}.get(health["overall"], "⚪")
    lines = [f"{emoji} System Status: {health['overall'].upper()} ({health['health_display']})"]
    for c in health["checks"]:
        icon = "✅" if c["status"] == "healthy" else "❌"
        lines.append(f"  {icon} {c['name']}: {c['status']} ({c['latency_ms']}ms)")
    return {"text": "\n".join(lines), "overall": health["overall"]}
