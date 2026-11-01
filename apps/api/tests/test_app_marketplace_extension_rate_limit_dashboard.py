from app.services.app_marketplace_extension_rate_limit_dashboard import RateLimitDashboardService

def test_configure_and_check():
    svc = RateLimitDashboardService()
    svc.configure("c1", "/api/data", 5, 60)
    ok, remaining = svc.check_and_record("c1", "/api/data")
    assert ok is True
    assert remaining == 4

def test_rate_limited():
    svc = RateLimitDashboardService()
    svc.configure("c1", "/api/data", 3, 60)
    for _ in range(3):
        svc.check_and_record("c1", "/api/data")
    ok, remaining = svc.check_and_record("c1", "/api/data")
    assert ok is False
    assert remaining == 0

def test_auto_defaults():
    svc = RateLimitDashboardService()
    ok, _ = svc.check_and_record("c1", "/api/new", "POST")
    assert ok is True

def test_dashboard():
    svc = RateLimitDashboardService()
    svc.configure("c1", "/a", 10, 60)
    svc.configure("c1", "/b", 20, 60)
    dash = svc.get_dashboard("c1")
    assert len(dash) == 2
