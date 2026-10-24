"""Usage meter — visual usage meters for quotas and limits."""
from __future__ import annotations


def build_meter(*, label: str, used: float, limit: float, unit: str = "") -> dict:
    pct = round(used / max(limit, 0.01) * 100, 1)
    status = "critical" if pct >= 90 else "warning" if pct >= 75 else "ok"
    remaining = max(0, limit - used)
    return {
        "label": label, "used": used, "limit": limit, "unit": unit,
        "pct": pct, "status": status, "remaining": remaining,
        "display": f"{used:,.0f} / {limit:,.0f} {unit}".strip(),
        "remaining_display": f"{remaining:,.0f} {unit}".strip(),
    }


def build_meters(items: list[dict]) -> dict:
    meters = [build_meter(**i) for i in items]
    critical = sum(1 for m in meters if m["status"] == "critical")
    return {"meters": meters, "total": len(meters), "critical_count": critical,
            "all_ok": critical == 0}
