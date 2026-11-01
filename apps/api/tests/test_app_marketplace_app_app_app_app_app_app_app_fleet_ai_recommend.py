from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_recommend import fleet_ai_recommendation
def test_rec():
    r = fleet_ai_recommendation([{"active": True, "requests_24h": 20000000, "ctr_pct": 12.5, "items": 1000000}])
    assert r["ctr"] == 12.5
    assert r["engaging"]
