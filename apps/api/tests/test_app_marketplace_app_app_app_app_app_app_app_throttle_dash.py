from app.services.app_marketplace_app_app_app_app_app_app_app_throttle_dash import throttle_dashboard

def test_dashboard():
    r = throttle_dashboard([
        {"tenant_id": "t1", "throttled": False}, {"tenant_id": "t1", "throttled": False},
        {"tenant_id": "t1", "throttled": True},
        {"tenant_id": "t2", "throttled": True}, {"tenant_id": "t2", "throttled": True},
    ])
    assert r["total_throttled"] == 3
    assert r["total_allowed"] == 2
    assert r["tenants"][0]["tenant_id"] == "t2"  # most throttled
    assert r["tenants"][0]["throttle_rate"] == 100.0
