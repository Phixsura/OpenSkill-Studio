from app.services.app_developer_app_analytics_builder import build_app_analytics

def test_build():
    a = build_app_analytics(
        app={"name": "X", "slug": "x"},
        install_trend=[{"date": "2026-01", "net": 5}],
        execution_stats={"total": 100},
        webhook_stats={"success_rate": 99},
        health_trend={"trend": "stable", "current": 95},
    )
    assert a["app"]["name"] == "X"
    assert len(a["sections"]) == 4
    assert a["health_trend"]["current"] == 95
