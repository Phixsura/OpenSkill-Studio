"""Developer API status — real-time API health status page data."""

from datetime import UTC, datetime


def build_api_status(*, services: list[dict]) -> dict:
    """Build API status page data."""
    all_up = all(s.get("status") == "operational" for s in services)
    degraded = any(s.get("status") == "degraded" for s in services)
    return {
        "overall": "operational" if all_up else "degraded" if degraded else "outage",
        "services": services,
        "last_checked": datetime.now(UTC).isoformat(),
        "uptime_pct": round(sum(s.get("uptime_pct", 100) for s in services) / len(services), 2) if services else 100,
    }


DEFAULT_SERVICES = [
    {"name": "Developer API", "status": "operational", "uptime_pct": 99.99},
    {"name": "Sandbox Execution", "status": "operational", "uptime_pct": 99.95},
    {"name": "Webhook Delivery", "status": "operational", "uptime_pct": 99.98},
    {"name": "Marketplace", "status": "operational", "uptime_pct": 99.99},
    {"name": "OAuth", "status": "operational", "uptime_pct": 100.0},
]
