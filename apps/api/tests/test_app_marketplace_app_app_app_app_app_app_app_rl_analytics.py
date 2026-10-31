from app.services.app_marketplace_app_app_app_app_app_app_app_rl_analytics import analyze_rate_limits

def test_analytics():
    r = analyze_rate_limits([
        {"tenant_id": "t1", "allowed": True}, {"tenant_id": "t1", "allowed": True},
        {"tenant_id": "t1", "allowed": False},
        {"tenant_id": "t2", "allowed": False}, {"tenant_id": "t2", "allowed": False},
    ])
    assert r["total_denied"] == 3
    assert r["total_allowed"] == 2
    assert r["tenants"][0]["tenant_id"] == "t2"  # most denied first
    assert r["tenants"][0]["deny_rate"] == 100.0
