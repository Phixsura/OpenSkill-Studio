from app.services.app_marketplace_app_developer_app_smart_routing import select_best_instance, compute_routing_stats, detect_hot_instance

def test_least_latency():
    instances = [{"id": "a", "health": "healthy", "avg_latency_ms": 200},
                 {"id": "b", "health": "healthy", "avg_latency_ms": 50},
                 {"id": "c", "health": "unhealthy", "avg_latency_ms": 10}]
    r = select_best_instance(instances=instances, strategy="least_latency")
    assert r["id"] == "b"

def test_no_healthy():
    instances = [{"id": "a", "health": "unhealthy"}]
    assert select_best_instance(instances=instances) is None

def test_stats():
    decisions = [{"instance_id": "a", "latency_ms": 100}, {"instance_id": "a", "latency_ms": 200},
                 {"instance_id": "b", "latency_ms": 50}]
    r = compute_routing_stats(decisions=decisions)
    assert r["total_decisions"] == 3

def test_hot_instance():
    stats = {"total_decisions": 100, "instances": [{"instance_id": "a", "requests": 80}]}
    r = detect_hot_instance(stats=stats)
    assert r is not None
    assert r["pct"] == 80.0

def test_no_hot():
    stats = {"total_decisions": 100, "instances": [{"instance_id": "a", "requests": 50}, {"instance_id": "b", "requests": 50}]}
    assert detect_hot_instance(stats=stats) is None
