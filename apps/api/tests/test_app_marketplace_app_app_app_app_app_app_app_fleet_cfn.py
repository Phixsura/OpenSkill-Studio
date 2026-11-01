from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cfn import fleet_cfn_status
def test_cfn():
    r = fleet_cfn_status([{"status": "CREATE_COMPLETE"}, {"status": "ROLLBACK_COMPLETE"}, {"status": "UPDATE_IN_PROGRESS"}])
    assert r["complete"] == 1
    assert r["rollback"] == 1
    assert not r["healthy"]
