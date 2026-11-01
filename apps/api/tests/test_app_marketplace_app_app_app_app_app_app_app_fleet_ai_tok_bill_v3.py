from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tok_bill_v3 import fleet_ai_token_billing_v3
def test_tbv3():
    r = fleet_ai_token_billing_v3([{"active": True, "tokens_24h": 100000000000, "revenue_usd": 500000, "customers": 10000}])
    assert r["revenue_usd"] == 500000
    assert r["billing"]
