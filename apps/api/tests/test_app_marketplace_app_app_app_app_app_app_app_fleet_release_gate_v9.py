from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_release_gate_v9 import fleet_release_gate_v9
def test_rg2_v9():
    r = fleet_release_gate_v9([{"all_gates_passed": True, "blocked": False, "gates": 5}])
    assert r["passed"] == 1
    assert r["healthy"]
