from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_openpolicy import fleet_openpolicy
def test_op():
    r = fleet_openpolicy([{"has_policy_tests": True, "policy_ci_enforced": True}] * 8 + [{"has_policy_tests": False}] * 2)
    assert r["coverage_pct"] == 80.0
    assert r["mature"]
