from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sast import fleet_sast_results
def test_sast():
    r = fleet_sast_results([{"findings": 10, "critical": 1, "high": 2}, {"findings": 5, "critical": 0, "high": 0}])
    assert r["total_findings"] == 15
    assert r["critical"] == 1
    assert not r["secure"]
