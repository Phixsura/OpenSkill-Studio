from app.services.app_marketplace_app_developer_app_data_retention_policy import create_retention_policy, compute_data_expiry, estimate_data_cleanup

def test_preset():
    p = create_retention_policy(app_id="a1", preset="gdpr_compliant")
    assert p["config"]["logs_days"] == 30

def test_invalid_preset():
    p = create_retention_policy(app_id="a1", preset="forever")
    assert p["error"]

def test_custom():
    p = create_retention_policy(app_id="a1", custom={"logs_days": 14})
    assert p["config"]["logs_days"] == 14

def test_expiry_future():
    r = compute_data_expiry(created_at="2026-10-01T00:00:00Z", retention_days=365)
    assert not r["expired"]
    assert r["days_remaining"] > 0

def test_expiry_past():
    r = compute_data_expiry(created_at="2020-01-01T00:00:00Z", retention_days=30)
    assert r["expired"]

def test_cleanup():
    r = estimate_data_cleanup(data_counts={"logs": 100000, "analytics": 50000},
                               policy={"logs_days": 30, "analytics_days": 180})
    assert r["logs"]["daily_cleanup"] > r["analytics"]["daily_cleanup"]
