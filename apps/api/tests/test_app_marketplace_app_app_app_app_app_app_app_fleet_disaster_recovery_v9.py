from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_disaster_recovery_v9 import fleet_disaster_recovery_v9
def test_dr_v9():
    r = fleet_disaster_recovery_v9([{"last_test_passed": True, "rpo_met": True, "rto_met": True}])
    assert r["tested"] == 1
    assert r["healthy"]
