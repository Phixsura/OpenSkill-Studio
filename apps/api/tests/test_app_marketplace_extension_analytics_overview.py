from app.services.app_marketplace_extension_analytics_overview import PlatformAnalyticsOverviewService


def test_overview():
    svc = PlatformAnalyticsOverviewService()
    svc.update(dau=5000, wau=12000, mau=30000, installs_today=500,
               revenue_today_cents=100000, api_calls_today=2000000,
               avg_session_minutes=15, retention_7d=45, nps_score=55)
    overview = svc.get_overview()
    assert overview["engagement"]["dau"] == 5000
    assert overview["engagement"]["dau_wau_ratio"] == 41.7
    assert overview["revenue"]["projected_monthly"] == 3000000


def test_health_indicators():
    svc = PlatformAnalyticsOverviewService()
    svc.update(dau=5000, wau=10000, retention_7d=50, nps_score=60)
    indicators = svc.get_health_indicators()
    assert any(i["status"] == "excellent" for i in indicators)
    assert len(indicators) >= 3


def test_low_engagement():
    svc = PlatformAnalyticsOverviewService()
    svc.update(dau=100, wau=1000, retention_7d=10, nps_score=-10)
    indicators = svc.get_health_indicators()
    assert any(i["status"] == "needs_work" for i in indicators)
