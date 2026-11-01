from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_expansion_v7 import fleet_ai_expansion_v7
def test_ev7():
    r = fleet_ai_expansion_v7([{"active": True, "markets": 10, "features": 100, "expansion_usd": 50000000}])
    assert r["markets"] == 10
    assert r["expanding"]
