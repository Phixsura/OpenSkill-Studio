from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_bill_v2 import fleet_ai_model_billing_v2
def test_mbv2():
    r = fleet_ai_model_billing_v2([{"active": True, "models": 300, "revenue_usd": 200000, "invoices": 5000}])
    assert r["revenue_usd"] == 200000
    assert r["monetized"]
