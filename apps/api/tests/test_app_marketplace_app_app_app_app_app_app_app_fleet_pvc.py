from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pvc import fleet_pvc_status
def test_pvc():
    r = fleet_pvc_status([{"status": "Bound"}, {"status": "Pending"}, {"status": "Lost"}])
    assert r["bound"] == 1
    assert r["lost"] == 1
    assert not r["healthy"]
