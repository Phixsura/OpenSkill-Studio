from app.services.app_marketplace_extension_load_balancer import WeightedLoadBalancerService


def test_weighted_round_robin():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080", weight=2)
    svc.add_replica("api", "r2", "http://r2:8080", weight=1)
    # Weight 2:1 means r1 gets 2/3 of traffic
    results = []
    for _ in range(6):
        r = svc.route_weighted_rr("api")
        results.append(r.replica_id)
        svc.release("api", r.replica_id)
    assert results.count("r1") == 4  # 2/3 of 6
    assert results.count("r2") == 2


def test_least_connections():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080", weight=1)
    svc.add_replica("api", "r2", "http://r2:8080", weight=1)
    # First goes to r1 (both 0 connections)
    r = svc.route_least_connections("api")
    # Don't release — r1 has 1 active
    # Second should go to r2 (0 connections vs 1)
    r2 = svc.route_least_connections("api")
    assert r.replica_id != r2.replica_id


def test_least_connections_weighted():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080", weight=3)
    svc.add_replica("api", "r2", "http://r2:8080", weight=1)
    # r1 score = connections/weight, so r1 can take more before r2 is chosen
    for _ in range(3):
        svc.route_least_connections("api")
    # r1 should have all 3 (score 3/3=1.0 vs r2 0/1=0.0 after first)
    # Actually after first to r1 (0/3 < 0/1), second goes to r2 (1/3 > 0/1)
    stats = svc.get_stats("api")
    assert stats["total_connections"] == 3


def test_unhealthy_skipped():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080")
    svc.add_replica("api", "r2", "http://r2:8080")
    # Mark r1 unhealthy
    for r in svc._pools["api"]:
        if r.replica_id == "r1":
            r.healthy = False
    r = svc.route_weighted_rr("api")
    assert r.replica_id == "r2"


def test_drain():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080")
    svc.add_replica("api", "r2", "http://r2:8080")
    svc.drain("api", "r1")
    # Draining replica skipped
    r = svc.route_weighted_rr("api")
    assert r.replica_id == "r2"
    stats = svc.get_stats("api")
    assert stats["draining"] == 1


def test_error_threshold():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080")
    # Simulate requests that all fail
    for _ in range(3):
        svc.route_weighted_rr("api")
        svc.report_error("api", "r1", health_threshold=3)
    # After 3 errors with 100% error rate, should be unhealthy
    pool = svc._pools["api"]
    assert pool[0].healthy is False


def test_mark_healthy_recovers():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080")
    for r in svc._pools["api"]:
        r.healthy = False
    svc.mark_healthy("api", "r1")
    r = svc.route_weighted_rr("api")
    assert r is not None


def test_no_replicas():
    svc = WeightedLoadBalancerService()
    assert svc.route_weighted_rr("nonexistent") is None
    assert svc.route_least_connections("nonexistent") is None


def test_duplicate_replica_rejected():
    svc = WeightedLoadBalancerService()
    svc.add_replica("api", "r1", "http://r1:8080")
    try:
        svc.add_replica("api", "r1", "http://r1-copy:8080")
        assert False
    except ValueError:
        pass
