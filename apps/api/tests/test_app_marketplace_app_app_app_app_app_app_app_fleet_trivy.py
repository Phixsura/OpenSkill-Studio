from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_trivy import fleet_trivy_status
def test_trivy():
    r = fleet_trivy_status([{"critical": 0, "high": 0}, {"critical": 1, "high": 3}])
    assert r["clean"] == 1
    assert r["critical"] == 1
    assert not r["all_clean"]
