from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_helm_release_v9 import fleet_helm_release_v9
def test_hr_v9():
    r = fleet_helm_release_v9([{"status": "deployed", "revision": 5}, {"status": "deployed", "revision": 3}])
    assert r["deployed"] == 2
    assert r["total_revisions"] == 8
    assert r["healthy"]
