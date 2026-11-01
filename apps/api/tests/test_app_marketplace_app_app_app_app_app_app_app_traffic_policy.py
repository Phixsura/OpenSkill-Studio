from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_policy import create_policy, evaluate_request, policy_stats

def test_evaluate():
    p = create_policy("api", [
        {"match": "/api/admin/*", "action": "deny", "priority": 1},
        {"match": "/*", "action": "allow", "priority": 100},
    ])
    r = evaluate_request(p, "/api/admin/users")
    assert r["action"] == "deny"
    r2 = evaluate_request(p, "/api/public")
    assert r2["action"] == "allow"

def test_stats():
    policies = [create_policy("a", [{"match": "/*"}] * 3), create_policy("b", [{"match": "/*"}] * 5)]
    s = policy_stats(policies)
    assert s["total_rules"] == 8
    assert s["avg_rules"] == 4.0
