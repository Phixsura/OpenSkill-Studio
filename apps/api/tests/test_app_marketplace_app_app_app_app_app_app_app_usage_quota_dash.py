from app.services.app_marketplace_app_app_app_app_app_app_app_usage_quota_dash import aggregate_quotas, top_consumers

def test_aggregate():
    r = aggregate_quotas([
        {"tenant_id": "t1", "used": 800, "limit": 1000},
        {"tenant_id": "t2", "used": 1200, "limit": 1000},
        {"tenant_id": "t3", "used": 100, "limit": 1000},
    ])
    assert r["exceeded"] == 1
    assert r["warning"] == 1
    assert r["tenants"] == 3

def test_top():
    r = top_consumers([
        {"tenant_id": "t1", "used": 500, "limit": 1000},
        {"tenant_id": "t2", "used": 900, "limit": 1000},
    ], limit=1)
    assert r[0]["tenant"] == "t2"
    assert r[0]["pct"] == 90.0
