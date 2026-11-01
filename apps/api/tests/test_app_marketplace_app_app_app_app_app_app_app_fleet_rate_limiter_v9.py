from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rate_limiter_v9 import fleet_rate_limiter_v9
def test_rl_v9():
    r = fleet_rate_limiter_v9([{"total_requests": 100000, "throttled_requests": 50}])
    assert r["throttle_pct"] == 0.05
    assert r["healthy"]
