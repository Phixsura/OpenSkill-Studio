from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ready_gate import fleet_ai_readiness_gate
def test_rg():
    r = fleet_ai_readiness_gate([{"active": True, "services": 100, "ready": 100, "checks": 10}])
    assert r["ready"] == 100
    assert r["all_ready"]
