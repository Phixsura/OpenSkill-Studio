from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rl_config import fleet_rl_config
def test_rl():
    r = fleet_rl_config([{"has_rate_limit": True}, {"has_rate_limit": False}, {"has_rate_limit": True}])
    assert r["protected"] == 2
    assert r["unprotected"] == 1
    assert not r["fully_covered"]
