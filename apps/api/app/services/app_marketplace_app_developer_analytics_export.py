"""Developer analytics export — comprehensive analytics data export."""

import json
from datetime import datetime, timezone


def build_analytics_export(*, app_id: str, period: str, sections: list[str]) -> dict:
    available = {"installs", "api_usage", "errors", "revenue", "retention", "geo", "funnel"}
    invalid = set(sections) - available
    if invalid:
        return {"error": f"Unknown sections: {', '.join(invalid)}"}
    return {"app_id": app_id, "period": period, "sections": sections,
            "format": "json", "status": "generating",
            "requested_at": datetime.now(timezone.utc).isoformat(), "error": None}


def format_export(*, data: dict, fmt: str = "json") -> str:
    if fmt == "json":
        return json.dumps(data, indent=2, default=str)
    # CSV header
    if not data.get("rows"):
        return ""
    headers = list(data["rows"][0].keys())
    lines = [",".join(headers)]
    for row in data["rows"]:
        lines.append(",".join(str(row.get(h, "")) for h in headers))
    return "\n".join(lines)
