from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ratelim_v2 import fleet_ai_rate_limiter_v2
def test_rl():
    r = fleet_ai_rate_limiter_v2([{"active": True, "throttled_24h": 5000, "total_24h": 10000000}])
    assert r["throttle_pct"] == 0.05
    assert r["fair"]
