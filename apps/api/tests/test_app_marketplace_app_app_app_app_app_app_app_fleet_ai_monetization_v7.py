from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_monetization_v7 import fleet_ai_monetization_v7
def test_mv7():
    r = fleet_ai_monetization_v7([{"active": True, "mrr_usd": 50000000, "arpu_usd": 500, "ltv_usd": 50000, "payback_m": 6}])
    assert r["mrr"] == 50000000
    assert r["profitable"]
