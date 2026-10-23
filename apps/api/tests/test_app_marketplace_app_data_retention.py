from app.services.app_marketplace_app_data_retention import get_retention_policies, estimate_storage_savings

def test_defaults():
    r = get_retention_policies()
    assert r["total"] == 6
    audit = next(p for p in r["policies"] if p["data_type"] == "audit_logs")
    assert audit["retention_days"] == 730
    assert not audit["is_custom"]

def test_overrides():
    r = get_retention_policies(custom_overrides={"api_logs": 30})
    api = next(p for p in r["policies"] if p["data_type"] == "api_logs")
    assert api["retention_days"] == 30
    assert api["is_custom"]

def test_storage():
    policies = [{"retention_days": 90}, {"retention_days": 30}]
    r = estimate_storage_savings(current_size_gb=100, policies=policies, avg_daily_growth_gb=0.5)
    assert r["estimated_deletable_gb"] > 0
    assert r["savings_pct"] > 0
