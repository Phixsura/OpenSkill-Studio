from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_helm import fleet_helm_status
def test_helm():
    r = fleet_helm_status([{"status": "deployed"}, {"status": "deployed"}, {"status": "failed"}])
    assert r["deployed"] == 2
    assert r["failed"] == 1
    assert not r["healthy"]
