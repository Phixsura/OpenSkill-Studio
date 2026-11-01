from app.services.app_marketplace_app_app_app_app_app_app_app_platform_overview import platform_overview, platform_stats_summary

def test_overview():
    r = platform_overview([
        {"name": "Extension SDK", "status": "operational", "services": 159, "components": 159},
        {"name": "Marketplace", "status": "operational", "services": 159, "components": 159},
        {"name": "Automation", "status": "operational", "services": 159, "components": 159},
    ])
    assert r["overall"] == "operational"
    assert r["health_pct"] == 100.0
    assert r["total_services"] == 477

def test_stats():
    r = platform_stats_summary()
    assert r["status"] == "FULLY OPERATIONAL"
    assert r["modules"] == 10
