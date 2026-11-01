from app.services.app_marketplace_extension_usage_quota_dashboard import UsageQuotaDashboardService

def test_set_and_record():
    svc = UsageQuotaDashboardService()
    svc.set_limit("u1", "api_calls", 1000)
    assert svc.record_usage("u1", "api_calls", 500) is True
    dash = svc.get_dashboard("u1")
    assert dash[0].percentage == 50.0

def test_exceeded():
    svc = UsageQuotaDashboardService()
    svc.set_limit("u1", "uploads", 5)
    for _ in range(5):
        svc.record_usage("u1", "uploads")
    assert svc.record_usage("u1", "uploads") is False
    assert svc.get_dashboard("u1")[0].is_exceeded is True

def test_warnings():
    svc = UsageQuotaDashboardService()
    svc.set_limit("u1", "api", 100)
    svc.record_usage("u1", "api", 85)
    assert len(svc.get_warnings("u1")) == 1

def test_reset():
    svc = UsageQuotaDashboardService()
    svc.set_limit("u1", "api", 100)
    svc.record_usage("u1", "api", 50)
    svc.reset("u1", "api")
    assert svc.get_dashboard("u1")[0].used == 0
