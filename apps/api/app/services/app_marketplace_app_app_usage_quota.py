"""Usage quota — resource consumption tracking with limits."""

import html


def build_usage_quota(*, resources: list[dict]) -> dict:
    items = []
    warnings = []
    for res in resources:
        name = html.escape(res.get("name", ""))
        used = res.get("used", 0)
        limit = res.get("limit", 0)
        pct = round(used / limit * 100, 1) if limit > 0 else 0
        status = "critical" if pct >= 90 else "warning" if pct >= 75 else "ok"
        if status in ("critical", "warning"):
            warnings.append({"name": name, "status": status, "pct": pct})
        items.append({"name": name, "used": used, "limit": limit,
                       "pct": pct, "status": status, "unit": res.get("unit", "")})
    return {"resources": items, "total": len(items), "warnings": warnings,
            "has_warnings": len(warnings) > 0}
