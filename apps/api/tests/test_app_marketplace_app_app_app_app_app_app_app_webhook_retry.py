from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_retry import (
    create_retry_queue, attempt_retry, retry_stats,
)

def test_retry_flow():
    e = create_retry_queue("wh1", "https://hook.com", '{"event":"test"}', max_retries=3)
    r1 = attempt_retry(e, False)
    assert not r1["delivered"]
    assert e["status"] == "retrying"
    attempt_retry(e, False)
    r3 = attempt_retry(e, False)
    assert r3["exhausted"]
    assert e["status"] == "failed"

def test_success():
    e = create_retry_queue("wh2", "https://hook.com", "{}")
    r = attempt_retry(e, True)
    assert r["delivered"]
    assert e["status"] == "delivered"

def test_stats():
    q = [
        create_retry_queue("a", "", ""),
        create_retry_queue("b", "", ""),
    ]
    q[0]["status"] = "delivered"
    s = retry_stats(q)
    assert s["delivered"] == 1
    assert s["delivery_rate"] == 50
