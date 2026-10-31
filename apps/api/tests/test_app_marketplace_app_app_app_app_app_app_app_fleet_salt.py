from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_salt import fleet_salt_status
def test_salt():
    r = fleet_salt_status([{"connected": True}, {"connected": False}])
    assert r["connected"] == 1
    assert r["disconnected"] == 1
    assert not r["healthy"]
