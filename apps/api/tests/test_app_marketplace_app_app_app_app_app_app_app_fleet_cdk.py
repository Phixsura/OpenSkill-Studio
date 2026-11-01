from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cdk import fleet_cdk_status
def test_cdk():
    r = fleet_cdk_status([{"status": "CREATE_COMPLETE"}, {"status": "UPDATE_COMPLETE", "drift_detected": True}])
    assert r["deployed"] == 2
    assert r["drifted"] == 1
    assert not r["healthy"]
