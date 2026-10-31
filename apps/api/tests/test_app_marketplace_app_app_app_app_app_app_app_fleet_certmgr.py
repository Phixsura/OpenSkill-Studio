from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_certmgr import fleet_certmgr_status
def test_cm():
    r = fleet_certmgr_status([{"ready": True, "days_to_expiry": 90}, {"ready": True, "days_to_expiry": 10, "renewal_failed": True}])
    assert r["expiring"] == 1
    assert r["failed_renewal"] == 1
    assert not r["healthy"]
