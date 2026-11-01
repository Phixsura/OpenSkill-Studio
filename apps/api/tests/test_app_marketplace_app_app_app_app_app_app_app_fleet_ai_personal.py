from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_personal import fleet_ai_personalization
def test_per():
    r = fleet_ai_personalization([{"active": True, "requests_24h": 20000000, "engagement_lift_pct": 25}])
    assert r["requests_24h"] == 20000000
    assert r["effective"]
