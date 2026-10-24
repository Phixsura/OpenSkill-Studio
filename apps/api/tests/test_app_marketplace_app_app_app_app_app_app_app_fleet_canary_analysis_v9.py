from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_canary_analysis_v9 import fleet_canary_analysis_v9
def test_cana_v9():
    r = fleet_canary_analysis_v9([{"result": "pass", "metrics_compared": 50}])
    assert r["passed"] == 1
    assert r["healthy"]
