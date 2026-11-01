"""App analytics overview — complete analytics summary for an app."""


def build_analytics_overview(*, app_id: str, metrics: dict, period: str = "30d") -> dict:
    installs = metrics.get("installs", 0)
    uninstalls = metrics.get("uninstalls", 0)
    net_installs = installs - uninstalls
    retention = metrics.get("retention_30d", 0)
    revenue = metrics.get("revenue", 0)
    api_calls = metrics.get("api_calls", 0)
    errors = metrics.get("errors", 0)
    error_rate = round(errors / max(api_calls, 1) * 100, 2)
    return {
        "app_id": app_id,
        "period": period,
        "acquisition": {"installs": installs, "uninstalls": uninstalls,
                         "net": net_installs, "growth_pct": round(net_installs / max(installs, 1) * 100, 1)},
        "engagement": {"dau": metrics.get("dau", 0), "wau": metrics.get("wau", 0),
                        "mau": metrics.get("mau", 0), "retention_30d": retention},
        "performance": {"api_calls": api_calls, "errors": errors,
                         "error_rate": error_rate, "avg_latency_ms": metrics.get("avg_latency_ms", 0)},
        "revenue": {"total": revenue, "mrr": metrics.get("mrr", 0),
                     "arpu": round(revenue / max(metrics.get("paying_users", 1), 1), 2)},
    }
