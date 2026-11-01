from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_retention_v9 import fleet_data_retention_v9
def test_dr2_v9():
    r = fleet_data_retention_v9([{"compliant": True, "expired_records": 0, "purged_records": 1000}])
    assert r["compliant"] == 1
    assert r["healthy"]
