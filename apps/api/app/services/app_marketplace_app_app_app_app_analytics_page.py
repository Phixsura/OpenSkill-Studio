"""App analytics page — complete analytics dashboard for app publishers."""

import html
from collections import defaultdict


def build_analytics_page(*, app_name: str, period: str = "30d",
                            installs: list[dict], api_calls: list[dict],
                            top_countries: list[dict] | None = None) -> dict:
    total_installs = sum(d.get("count", 0) for d in installs)
    total_api = sum(d.get("count", 0) for d in api_calls)
    install_trend = installs[-1].get("count", 0) - installs[0].get("count", 0) if len(installs) >= 2 else 0
    return {
        "app_name": html.escape(app_name), "period": period,
        "kpis": [
            {"label": "Total Installs", "value": total_installs, "display": f"{total_installs:,}", "icon": "📥"},
            {"label": "API Calls", "value": total_api, "display": f"{total_api:,}", "icon": "🔗"},
            {"label": "Install Trend", "value": install_trend,
             "display": f"+{install_trend}" if install_trend > 0 else str(install_trend), "icon": "📈"},
        ],
        "install_chart": [{"date": d.get("date", ""), "count": d.get("count", 0)} for d in installs],
        "api_chart": [{"date": d.get("date", ""), "count": d.get("count", 0)} for d in api_calls],
        "top_countries": [{"country": html.escape(c.get("country", "")),
                            "count": c.get("count", 0)} for c in (top_countries or [])[:5]],
    }
