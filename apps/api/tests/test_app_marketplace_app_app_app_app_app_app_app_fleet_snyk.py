from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_snyk import fleet_snyk_status
def test_snyk():
    r = fleet_snyk_status([{"critical": 0, "high": 0, "medium": 2}, {"critical": 1, "high": 2, "medium": 3}])
    assert r["clean"] == 1
    assert r["critical"] == 1
    assert not r["secure"]
