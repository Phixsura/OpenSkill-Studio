from app.services.app_marketplace_app_usage_quota_enforcement import enforce_quota, get_enforcement_summary

def test_allow():
    r = enforce_quota(resource="api_calls", current=500, limit=1000)
    assert r["action"] == "allow"
    assert r["remaining"] == 500

def test_warn_grace():
    r = enforce_quota(resource="api_calls", current=1050, limit=1000, grace_pct=10)
    assert r["action"] == "warn"
    assert r["overage"] == 50

def test_block():
    r = enforce_quota(resource="api_calls", current=1200, limit=1000, grace_pct=10)
    assert r["action"] == "block"

def test_unlimited():
    r = enforce_quota(resource="storage", current=99999, limit=0)
    assert r["action"] == "allow"
    assert r["unlimited"]

def test_summary():
    quotas = [{"resource": "api", "current": 500, "limit": 1000},
              {"resource": "storage", "current": 1050, "limit": 1000}]
    r = get_enforcement_summary(quotas=quotas)
    assert r["warned_count"] == 1
    assert not r["all_ok"]
