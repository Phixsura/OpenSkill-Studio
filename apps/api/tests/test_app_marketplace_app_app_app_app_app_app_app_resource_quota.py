from app.services.app_marketplace_app_app_app_app_app_app_app_resource_quota import get_quotas, check_quota

def test_quotas():
    r = get_quotas("pro")
    assert r["quotas"]["api_calls"]["limit"] == 50000
    assert r["quotas"]["webhooks"]["limit"] == 25
    assert not r["quotas"]["api_calls"]["unlimited"]

def test_check():
    r = check_quota("free", "api_calls", 900)
    assert r["allowed"]
    assert r["remaining"] == 100
    assert r["pct_used"] == 90
    r2 = check_quota("enterprise", "storage_mb", 999999)
    assert r2["allowed"]
    assert r2["unlimited"]
