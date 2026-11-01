from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gw_ratelimit import fleet_gw_ratelimit
def test_ratelimit():
    r = fleet_gw_ratelimit([{"requests_limited": 100, "requests_total": 1000}, {"requests_limited": 50, "requests_total": 500}])
    assert r["limited"] == 150
    assert r["limited_pct"] == 10.0
    assert r["excessive"]
