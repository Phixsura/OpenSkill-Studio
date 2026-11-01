from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_test_cov import fleet_test_coverage
def test_cov():
    r = fleet_test_coverage([{"total_lines": 1000, "covered_lines": 850}, {"total_lines": 2000, "covered_lines": 1500}])
    assert r["covered_lines"] == 2350
    assert r["coverage_pct"] == 78.3
    assert not r["meets_target"]
