"""Complete platform analytics FINAL — platform-wide analytics for operators."""

from collections import defaultdict


def build_platform_analytics_final(*, apps: list[dict], developers: list[dict],
                                        installs: list[dict], api_calls: int,
                                        revenue: dict, growth: dict) -> dict:
    by_category = defaultdict(int)
    for a in apps:
        by_category[a.get("category", "other")] += 1
    top_apps = sorted(apps, key=lambda a: -a.get("install_count", 0))[:10]
    top_devs = sorted(developers, key=lambda d: -d.get("total_installs", 0))[:10]
    return {
        "page_type": "platform_analytics",
        "overview": {
            "total_apps": len(apps), "total_developers": len(developers),
            "total_installs": len(installs), "api_calls_today": api_calls,
            "mrr": revenue.get("mrr", 0),
        },
        "growth": growth,
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        "top_apps": [{"name": a["name"], "installs": a.get("install_count", 0)} for a in top_apps],
        "top_developers": [{"name": d.get("display_name"), "installs": d.get("total_installs", 0)} for d in top_devs],
        "charts": ["installs_trend", "revenue_trend", "category_distribution", "geo_distribution"],
    }
