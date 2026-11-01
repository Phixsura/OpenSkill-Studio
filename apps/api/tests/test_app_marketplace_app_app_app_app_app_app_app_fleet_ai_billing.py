from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_billing import fleet_ai_billing
def test_bill():
    r = fleet_ai_billing([{"active": True, "revenue_usd": 50000, "invoices": 1000, "customers": 500}])
    assert r["revenue_usd"] == 50000
    assert r["monetized"]
