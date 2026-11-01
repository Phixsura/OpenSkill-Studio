from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sonarqube import fleet_sonarqube_status
def test_sq():
    r = fleet_sonarqube_status([{"quality_gate": "OK", "coverage_pct": 80}, {"quality_gate": "ERROR", "coverage_pct": 50}])
    assert r["passing"] == 1
    assert r["avg_coverage"] == 65.0
    assert not r["all_passing"]
