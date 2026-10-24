from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_policy import create_traffic_policy, evaluate_mesh_policies

def test_policy():
    p = create_traffic_policy("api-to-db", "api", "db", timeout_ms=5000, retries=2, circuit_breaker=True)
    assert p["timeout_ms"] == 5000
    assert p["circuit_breaker"]

def test_evaluate():
    policies = [
        create_traffic_policy("a", "api", "db", circuit_breaker=True),
        create_traffic_policy("b", "api", "cache", circuit_breaker=False),
        create_traffic_policy("c", "web", "api", circuit_breaker=True),
    ]
    r = evaluate_mesh_policies(policies)
    assert r["total_policies"] == 3
    assert r["with_circuit_breaker"] == 2
    assert r["cb_coverage_pct"] == 67
