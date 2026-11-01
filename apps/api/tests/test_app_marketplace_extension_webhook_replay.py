from app.services.app_marketplace_extension_webhook_replay import WebhookReplayService

def test_record_and_replay():
    svc = WebhookReplayService()
    evt = svc.record("https://api.example.com/hook", {"type": "install"}, "failed", 500)
    ok, msg = svc.replay(evt.event_id)
    assert ok is True
    assert evt.status == "replayed"
    assert evt.attempts == 2

def test_max_retries():
    svc = WebhookReplayService()
    evt = svc.record("https://api.example.com/hook", {}, "failed")
    for _ in range(4):
        svc.replay(evt.event_id)
    ok, msg = svc.replay(evt.event_id)
    assert ok is False
    assert "Max retries" in msg

def test_failed_list():
    svc = WebhookReplayService()
    svc.record("https://a.com/hook", {}, "delivered")
    svc.record("https://b.com/hook", {}, "failed", 500)
    assert len(svc.get_failed()) == 1

def test_stats():
    svc = WebhookReplayService()
    svc.record("https://a.com", {}, "delivered")
    svc.record("https://b.com", {}, "failed")
    svc.record("https://c.com", {}, "failed")
    stats = svc.get_stats()
    assert stats["delivered"] == 1
    assert stats["failed"] == 2
