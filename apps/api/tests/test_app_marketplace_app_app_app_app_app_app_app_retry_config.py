from app.services.app_marketplace_app_app_app_app_app_app_app_retry_config import get_policy, compute_retry_schedule, list_policies

def test_policy():
    p = get_policy("aggressive")
    assert p["max_retries"] == 10
    assert p["strategy"] == "exponential"

def test_schedule():
    s = compute_retry_schedule("standard")
    assert len(s) == 5
    assert s[0]["delay_ms"] == 5000
    assert s[1]["delay_ms"] == 10000

def test_list():
    assert len(list_policies()) == 4
