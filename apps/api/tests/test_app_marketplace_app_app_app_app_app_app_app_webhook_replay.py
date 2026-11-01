from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_replay import WebhookReplayQueue

def test_replay():
    q = WebhookReplayQueue()
    e = q.enqueue(url="https://example.com/hook", payload={"event": "test"},
                   status_code=500, error="Internal Server Error")
    assert e["queued"]
    r = q.replay(e["id"], success=False, status_code=503)
    assert not r["success"]
    assert r["retry"] == 1
    r2 = q.replay(e["id"], success=True, status_code=200)
    assert r2["success"]
    assert r2["removed"]
    assert q.stats()["queue_size"] == 0
