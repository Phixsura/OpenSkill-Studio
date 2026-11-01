from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_zookeeper import fleet_zookeeper_status
def test_zk():
    r = fleet_zookeeper_status([{"role": "leader", "avg_latency_ms": 2}, {"role": "follower", "avg_latency_ms": 3}, {"role": "follower", "avg_latency_ms": 4}])
    assert r["leader"] == 1
    assert r["quorum"]
    assert r["avg_latency_ms"] == 3.0
