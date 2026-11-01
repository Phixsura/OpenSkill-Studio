from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kafka import fleet_kafka_status
def test_kafka():
    r = fleet_kafka_status([{"online": True, "under_replicated_partitions": 0, "topics": 50}, {"online": True, "under_replicated_partitions": 5, "topics": 50}])
    assert r["online"] == 2
    assert r["under_replicated"] == 5
    assert not r["healthy"]
