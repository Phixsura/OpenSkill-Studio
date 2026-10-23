"""API status — real-time status of all API endpoints."""


def get_api_status(*, endpoints: list[dict]) -> dict:
    operational = sum(1 for e in endpoints if e.get("status") == "operational")
    degraded = sum(1 for e in endpoints if e.get("status") == "degraded")
    down = sum(1 for e in endpoints if e.get("status") == "down")
    overall = "operational" if down == 0 and degraded == 0 else "degraded" if down == 0 else "major_outage"
    return {"overall": overall, "operational": operational, "degraded": degraded, "down": down,
            "total": len(endpoints), "endpoints": endpoints}


def build_status_badge_svg(*, status: str) -> str:
    colors = {"operational": "#22c55e", "degraded": "#eab308", "major_outage": "#ef4444"}
    color = colors.get(status, "#6b7280")
    label = status.replace("_", " ").title()
    return f'<svg><rect fill="{color}"/><text>{label}</text></svg>'
