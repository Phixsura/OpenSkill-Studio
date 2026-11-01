from app.services.app_marketplace_app_app_app_app_app_app_app_sla_credit import calculate_credit

def test_met():
    r = calculate_credit(99.99, 99.9, 10000)
    assert r["sla_met"]
    assert r["credit_amount"] == 0

def test_minor_breach():
    r = calculate_credit(99.5, 99.9, 10000)
    assert not r["sla_met"]
    assert r["credit_pct"] == 10
    assert r["credit_amount"] == 1000

def test_major_breach():
    r = calculate_credit(90.0, 99.9, 10000)
    assert r["credit_pct"] == 50
    assert r["credit_amount"] == 5000
