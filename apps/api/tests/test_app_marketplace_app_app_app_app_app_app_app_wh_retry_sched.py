from app.services.app_marketplace_app_app_app_app_app_app_app_wh_retry_sched import WebhookRetryScheduler

def test_schedule():
    ws = WebhookRetryScheduler(max_retries=3, base_delay_ms=100)
    r = ws.schedule_retry("w1", 0, "https://example.com")
    assert r["scheduled"]
    assert r["delay_ms"] == 100
    r2 = ws.schedule_retry("w1", 1, "https://example.com")
    assert r2["delay_ms"] == 200

def test_max_retries():
    ws = WebhookRetryScheduler(max_retries=2)
    r = ws.schedule_retry("w1", 2, "https://example.com")
    assert not r["scheduled"]

def test_complete():
    ws = WebhookRetryScheduler()
    ws.schedule_retry("w1", 0, "url")
    ws.complete("w1", True)
    s = ws.stats()
    assert s["pending"] == 0
    assert s["succeeded"] == 1
