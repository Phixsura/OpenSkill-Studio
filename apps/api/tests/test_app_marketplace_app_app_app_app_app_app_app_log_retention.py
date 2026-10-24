from app.services.app_marketplace_app_app_app_app_app_app_app_log_retention import create_policy, evaluate_retention

def test_evaluate():
    policies = [create_policy("default", 30, ["api-logs", "web-logs"])]
    usage = {
        "api-logs": {"oldest_days": 90, "size_gb": 50},
        "web-logs": {"oldest_days": 20, "size_gb": 10},
    }
    r = evaluate_retention(policies, usage)
    assert r["action_count"] == 1  # only api-logs over retention
    assert r["total_reclaimable_gb"] > 0
    assert r["actions"][0]["source"] == "api-logs"
