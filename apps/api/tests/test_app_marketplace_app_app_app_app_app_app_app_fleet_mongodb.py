from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mongodb import fleet_mongodb_status
def test_mongo():
    r = fleet_mongodb_status([{"state": "PRIMARY"}, {"state": "SECONDARY", "replication_lag_sec": 2}])
    assert r["primary"] == 1
    assert r["healthy"]
