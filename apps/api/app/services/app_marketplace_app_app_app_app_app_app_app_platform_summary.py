"""Platform summary — generate executive platform summary reports."""
from __future__ import annotations


def generate_summary(metrics: dict) -> dict:
    apps = metrics.get("apps", 0)
    users = metrics.get("users", 0)
    revenue = metrics.get("monthly_revenue", 0)
    uptime = metrics.get("uptime_pct", 99.9)
    growth_pct = metrics.get("growth_pct", 0)
    health = "excellent" if uptime >= 99.9 and growth_pct > 0 else "good" if uptime >= 99.5 else "needs_attention"
    return {"apps": apps, "users": users, "revenue": revenue, "uptime": uptime,
            "growth_pct": growth_pct, "health": health,
            "highlights": _build_highlights(metrics),
            "display_revenue": f"${revenue:,.0f}"}


def _build_highlights(m: dict) -> list[str]:
    highlights = []
    if m.get("new_apps", 0) > 0:
        highlights.append(f"{m['new_apps']} new apps this month")
    if m.get("uptime_pct", 0) >= 99.99:
        highlights.append("Four nines uptime achieved")
    if m.get("growth_pct", 0) > 10:
        highlights.append(f"{m['growth_pct']}% month-over-month growth")
    return highlights


def compare_periods(current: dict, previous: dict) -> dict:
    deltas = {}
    for key in ("apps", "users", "monthly_revenue"):
        c = current.get(key, 0)
        p = previous.get(key, 0)
        deltas[key] = {"current": c, "previous": p, "delta": c - p,
                        "pct_change": round((c - p) / max(p, 1) * 100, 1)}
    return {"deltas": deltas, "improving": all(d["delta"] >= 0 for d in deltas.values())}
