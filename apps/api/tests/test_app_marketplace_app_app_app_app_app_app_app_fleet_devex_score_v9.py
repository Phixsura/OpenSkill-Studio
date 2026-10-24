from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_devex_score_v9 import fleet_devex_score_v9
def test_devex_v9():
    r = fleet_devex_score_v9([{"devex_score": 92, "avg_build_sec": 45, "avg_deploy_sec": 30}])
    assert r["avg_devex_score"] == 92.0
    assert r["healthy"]
