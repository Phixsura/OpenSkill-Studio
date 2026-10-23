"""Marketplace summary stats — the final stats aggregator for the entire platform."""

def compute_marketplace_summary(*, apps: int, developers: int, installs: int,
                                    reviews: int, api_calls: int, uptime_pct: float) -> dict:
    return {
        "headline_stats": [
            {"label": "Apps", "value": apps, "icon": "📦"},
            {"label": "Developers", "value": developers, "icon": "👨‍💻"},
            {"label": "Installations", "value": installs, "icon": "📥"},
            {"label": "Reviews", "value": reviews, "icon": "⭐"},
            {"label": "API Calls", "value": api_calls, "icon": "🌐"},
        ],
        "health": {"uptime_pct": uptime_pct, "status": "healthy" if uptime_pct >= 99.9 else "degraded"},
        "growth": {"apps_per_month": round(apps / 12), "installs_per_month": round(installs / 12)},
    }
