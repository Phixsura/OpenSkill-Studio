from app.services.app_marketplace_app_app_app_app_app_app_app_grand_summary import platform_summary, platform_health_report

def test_summary():
    r = platform_summary()
    assert r["all_operational"]
    assert len(r["modules"]) == 10
    assert r["total_services"] == 1480
    assert "250K" in r["milestone"]

def test_health():
    r = platform_health_report()
    assert r["overall"] == "healthy"
    assert r["uptime_pct"] >= 99.9
