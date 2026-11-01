from app.services.app_marketplace_app_load_balancer import round_robin, consistent_hash, get_instance_weights, health_check_summary

def test_round_robin():
    instances = [{"id": "a", "status": "healthy"}, {"id": "b", "status": "healthy"}]
    assert round_robin(instances=instances, request_index=0)["id"] == "a"
    assert round_robin(instances=instances, request_index=1)["id"] == "b"
    assert round_robin(instances=instances, request_index=2)["id"] == "a"

def test_skip_unhealthy():
    instances = [{"id": "a", "status": "unhealthy"}, {"id": "b", "status": "healthy"}]
    assert round_robin(instances=instances, request_index=0)["id"] == "b"

def test_consistent():
    instances = [{"id": "a", "status": "healthy"}, {"id": "b", "status": "healthy"}]
    r1 = consistent_hash(key="user1", instances=instances)
    r2 = consistent_hash(key="user1", instances=instances)
    assert r1["id"] == r2["id"]

def test_weights():
    instances = [{"id": "a", "capacity": 3}, {"id": "b", "capacity": 1}]
    w = get_instance_weights(instances=instances)
    assert w[0]["weight_pct"] == 75.0

def test_health():
    instances = [{"status": "healthy"}] * 3 + [{"status": "unhealthy"}]
    h = health_check_summary(instances=instances)
    assert h["healthy"] == 3
    assert h["availability_pct"] == 75.0
