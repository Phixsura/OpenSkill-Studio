from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ci_build import fleet_ci_build_time
def test_ci():
    r = fleet_ci_build_time([{"duration_sec": 200}, {"duration_sec": 400}, {"duration_sec": 800}])
    assert r["avg_sec"] == 466.7
    assert r["slow_builds"] == 1
    assert not r["fast"]
