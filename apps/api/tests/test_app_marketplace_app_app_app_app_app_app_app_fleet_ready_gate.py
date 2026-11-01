from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ready_gate import fleet_readiness_gate
def test_gate():
    r = fleet_readiness_gate([{"gates_passed": True}, {"gate_blocked": True}, {"gates_passed": True}])
    assert r["passed"] == 2
    assert r["blocked"] == 1
    assert not r["all_clear"]
