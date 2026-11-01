from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dast import fleet_dast_results
def test_dast():
    r = fleet_dast_results([{"vulnerabilities": 5, "critical": 0}, {"vulnerabilities": 3, "critical": 1}])
    assert r["total_vulns"] == 8
    assert not r["secure"]
