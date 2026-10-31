from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_market_v7 import fleet_ai_market_v7
def test_mv7():
    r = fleet_ai_market_v7([{"active": True, "share_pct": 35, "tam_usd": 50000000000, "competitors": 20, "win_pct": 70}])
    assert r["share"] == 35.0
    assert r["leading"]
