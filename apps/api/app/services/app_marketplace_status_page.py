"""Status page — public health dashboard for marketplace apps."""

from datetime import datetime, timezone


def build_status_page(*, services: list[dict], incidents: list[dict]) -> dict:
    all_ok = all(s.get("status") == "operational" for s in services)
    active_incidents = [i for i in incidents if i.get("status") != "resolved"]
    overall = "all_operational" if all_ok and not active_incidents else \
              "major_outage" if any(s.get("status") == "major_outage" for s in services) else \
              "partial_outage"
    return {
        "overall_status": overall, "services": services,
        "active_incidents": active_incidents, "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def build_service_status(*, name: str, uptime_pct: float, response_time_ms: int) -> dict:
    if uptime_pct >= 99.9:
        status = "operational"
    elif uptime_pct >= 99.0:
        status = "degraded"
    else:
        status = "major_outage"
    return {"name": name, "status": status, "uptime_pct": uptime_pct, "response_time_ms": response_time_ms}


def build_uptime_bars(*, daily_uptimes: list[dict]) -> list[dict]:
    return [{"date": d["date"],
             "color": "green" if d["uptime_pct"] >= 99.9 else "yellow" if d["uptime_pct"] >= 99 else "red",
             "uptime_pct": d["uptime_pct"]} for d in daily_uptimes[-90:]]
