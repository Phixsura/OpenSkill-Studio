from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_quality_gate_v9 import fleet_api_quality_gate_v9
def test_aqg2_v9():
    r = fleet_api_quality_gate_v9([{"passed": True, "blocked": False, "checks": 10}])
    assert r["passed"] == 1
    assert r["healthy"]
