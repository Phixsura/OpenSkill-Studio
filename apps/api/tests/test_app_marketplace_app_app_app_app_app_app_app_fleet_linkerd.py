from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_linkerd import fleet_linkerd_status
def test_linkerd():
    r = fleet_linkerd_status([{"meshed": True, "success_rate": 99.5}, {"meshed": True, "success_rate": 98}, {"meshed": False}])
    assert r["meshed"] == 2
    assert r["avg_success_rate"] == 98.8
    assert not r["healthy"]
