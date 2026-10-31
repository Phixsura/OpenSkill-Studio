from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dynamodb import fleet_dynamodb_status
def test_ddb():
    r = fleet_dynamodb_status([{"status": "ACTIVE", "throttled_reads": 0, "consumed_rcu": 5000}, {"status": "ACTIVE", "throttled_reads": 10, "consumed_rcu": 3000}])
    assert r["throttled"] == 1
    assert not r["healthy"]
