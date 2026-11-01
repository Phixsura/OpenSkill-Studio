from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_deploy_gate import fleet_ai_deployment_gate
def test_dg():
    r = fleet_ai_deployment_gate([{"active": True, "evals_24h": 100, "passed": 95, "blocked": 5, "checks": 15}])
    assert r["passed"] == 95
    assert r["guarding"]
