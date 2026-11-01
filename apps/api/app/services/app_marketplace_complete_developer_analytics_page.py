"""Complete developer analytics — cross-app analytics dashboard."""


def build_complete_developer_analytics(*, apps: list[dict], total_installs: int,
                                            total_api_calls: int, avg_rating: float,
                                            revenue: dict | None, top_apps: list[dict],
                                            install_trend: dict, error_rate: float) -> dict:
    return {
        "page_type": "developer_analytics",
        "overview": [
            {"label": "Total Installs", "value": total_installs, "icon": "📥"},
            {"label": "API Calls (30d)", "value": total_api_calls, "icon": "🌐"},
            {"label": "Avg Rating", "value": f"{avg_rating:.1f} ★", "icon": "⭐"},
            {"label": "Error Rate", "value": f"{error_rate:.2f}%", "icon": "❌"},
            {"label": "Apps", "value": len(apps), "icon": "📦"},
        ] + ([{"label": "MRR", "value": revenue.get("mrr", "$0"), "icon": "💰"}] if revenue else []),
        "charts": [
            {"key": "installs", "title": "Install Trend", "type": "line", "data": install_trend},
            {"key": "top_apps", "title": "Top Apps by Installs", "type": "bar", "data": top_apps[:5]},
        ],
        "time_ranges": ["7d", "30d", "90d", "12m"],
        "export_formats": ["csv", "json", "pdf"],
    }
