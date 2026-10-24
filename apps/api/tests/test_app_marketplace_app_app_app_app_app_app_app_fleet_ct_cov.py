from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ct_cov import fleet_contract_test_coverage
def test_ct():
    r = fleet_contract_test_coverage([{"has_contract_tests": True}] * 8 + [{"has_contract_tests": False}] * 2)
    assert r["coverage_pct"] == 80.0
    assert r["good"]
