from app.services.app_billing_summary import build_billing_summary

def test_basic():
    b = build_billing_summary(executions=1000, webhooks=500, api_calls=5000, storage_mb=100)
    assert b["total_usd"] > 0
    assert len(b["items"]) == 4

def test_premium_cheaper():
    std = build_billing_summary(executions=1000, webhooks=500, api_calls=5000, storage_mb=100, tier="standard")
    prem = build_billing_summary(executions=1000, webhooks=500, api_calls=5000, storage_mb=100, tier="premium")
    assert prem["total_usd"] <= std["total_usd"]

def test_zero():
    b = build_billing_summary(executions=0, webhooks=0, api_calls=0, storage_mb=0)
    assert b["total_usd"] == 0
