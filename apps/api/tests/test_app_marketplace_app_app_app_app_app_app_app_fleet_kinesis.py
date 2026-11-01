from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kinesis import fleet_kinesis_status
def test_kin():
    r = fleet_kinesis_status([{"status": "ACTIVE", "shards": 10, "records_per_sec": 50000}])
    assert r["shards"] == 10
    assert r["all_active"]
