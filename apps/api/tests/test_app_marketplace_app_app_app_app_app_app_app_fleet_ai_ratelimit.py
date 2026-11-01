from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ratelimit import fleet_ai_ratelimit
def test_rl():
    r = fleet_ai_ratelimit([{"active": True, "throttled_24h": 1000, "requests_24h": 1000000}])
    assert r["throttled_24h"] == 1000
    assert r["effective"]
