from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_queue_broker_v9 import fleet_queue_broker_v9
def test_queue_v9():
    r = fleet_queue_broker_v9([{"depth": 100, "msg_per_sec": 5000, "dead_letters": 0}])
    assert r["throughput"] == 5000
    assert r["dead_letters"] == 0
    assert r["healthy"]
