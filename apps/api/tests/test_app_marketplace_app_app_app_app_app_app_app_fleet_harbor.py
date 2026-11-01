from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_harbor import fleet_harbor_status
def test_harbor():
    r = fleet_harbor_status([{"repos": 50, "artifacts": 500}, {"repos": 30, "artifacts": 300, "over_quota": True}])
    assert r["repos"] == 80
    assert r["over_quota"] == 1
    assert not r["healthy"]
