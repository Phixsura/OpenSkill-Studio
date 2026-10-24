from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_saga import fleet_saga_status
def test_saga():
    r = fleet_saga_status([{"status": "completed"}, {"status": "compensating"}, {"status": "failed"}])
    assert r["completed"] == 1
    assert r["compensating"] == 1
    assert not r["healthy"]
