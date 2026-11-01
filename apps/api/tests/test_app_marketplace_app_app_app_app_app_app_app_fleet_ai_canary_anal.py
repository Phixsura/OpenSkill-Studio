from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_canary_anal import fleet_ai_canary_analysis
def test_ca():
    r = fleet_ai_canary_analysis([{"active": True, "analyses_24h": 50, "promoted": 48, "rolled_back": 0}])
    assert r["promoted"] == 48
    assert r["safe"]
