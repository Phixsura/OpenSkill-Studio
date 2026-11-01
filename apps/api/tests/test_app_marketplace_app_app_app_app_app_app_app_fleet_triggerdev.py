from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_triggerdev import fleet_triggerdev_status
def test_td():
    r = fleet_triggerdev_status([{"active": True, "runs_24h": 50000, "tasks": 100}])
    assert r["runs_24h"] == 50000
    assert r["productive"]
