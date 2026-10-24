from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_quality_gate import fleet_ai_quality_gate
def test_qg():
    r = fleet_ai_quality_gate([{"active": True, "evals_24h": 500, "passed": 480, "blocked": 20, "checks": 15}])
    assert r["passed"] == 480
    assert r["enforcing"]
