"""Developer analytics overview — aggregate all analytics for a developer."""
from __future__ import annotations


def build_developer_analytics(*, developer_id: str, apps: list[dict],
                                 period: str = "30d") -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_api = sum(a.get("api_calls", 0) for a in apps)
    total_revenue = sum(a.get("revenue", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    top_app = max(apps, key=lambda a: a.get("installs", 0)) if apps else None
    return {
        "developer_id": developer_id, "period": period,
        "app_count": len(apps),
        "total_installs": total_installs, "installs_display": f"{total_installs:,}",
        "total_api_calls": total_api, "api_display": f"{total_api:,}",
        "total_revenue": total_revenue, "revenue_display": f"${total_revenue:,.0f}",
        "avg_rating": avg_rating,
        "top_app": {"name": top_app.get("name", ""), "installs": top_app.get("installs", 0)} if top_app else None,
        "growth_areas": _identify_growth(apps),
    }


def _identify_growth(apps: list[dict]) -> list[str]:
    areas = []
    low_rated = [a for a in apps if a.get("rating", 5) < 4]
    if low_rated:
        areas.append(f"{len(low_rated)} app(s) below 4.0 rating")
    high_error = [a for a in apps if a.get("error_rate", 0) > 2]
    if high_error:
        areas.append(f"{len(high_error)} app(s) with high error rate")
    return areas
