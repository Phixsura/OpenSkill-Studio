from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_revenue_v2 import fleet_ai_revenue_v2
def test_rv2():
    r = fleet_ai_revenue_v2([{"active": True, "mrr_usd": 10000000, "growth_pct": 30, "ndr_pct": 130}])
    assert r["arr"] == 120000000
    assert r["scaling"]
