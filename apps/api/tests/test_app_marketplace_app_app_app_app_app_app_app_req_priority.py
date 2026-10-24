from app.services.app_marketplace_app_app_app_app_app_app_app_req_priority import classify_priority, priority_stats

def test_classify():
    rules = [
        {"name": "vip", "priority": "critical", "conditions": [{"field": "user_tier", "op": "eq", "value": "enterprise"}]},
        {"name": "health", "priority": "high", "conditions": [{"field": "path", "op": "contains", "value": "/health"}]},
    ]
    r = classify_priority({"user_tier": "enterprise", "path": "/api"}, rules)
    assert r["priority"] == "critical"
    r2 = classify_priority({"user_tier": "free", "path": "/health"}, rules)
    assert r2["priority"] == "high"
    r3 = classify_priority({"user_tier": "free", "path": "/api"}, rules)
    assert r3["priority"] == "normal"

def test_stats():
    r = priority_stats([{"priority": "critical"}, {"priority": "normal"}, {"priority": "normal"}])
    assert r["by_priority"]["critical"] == 1
    assert r["by_priority"]["normal"] == 2
