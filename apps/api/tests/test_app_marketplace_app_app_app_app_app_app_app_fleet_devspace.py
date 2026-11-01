from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_devspace import fleet_devspace_status
def test_ds():
    r = fleet_devspace_status([{"active": True}, {"active": False, "sleeping": True}])
    assert r["active"] == 1
    assert r["sleeping"] == 1
    assert r["cost_saving"]
