"""Webhook delivery queue tests."""
from app.services.app_webhook_queue import enqueue_delivery, dequeue_delivery, get_queue_size, clear_queue

def test_enqueue_dequeue():
    e = enqueue_delivery(app_id="wq1", event_type="test", url="https://x.com", payload={})
    assert e["status"] == "queued"
    d = dequeue_delivery("wq1")
    assert d is not None

def test_priority_order():
    enqueue_delivery(app_id="wq2", event_type="low", url="u", payload={}, priority=10)
    enqueue_delivery(app_id="wq2", event_type="high", url="u", payload={}, priority=1)
    d = dequeue_delivery("wq2")
    assert d["event_type"] == "high"

def test_empty_dequeue():
    assert dequeue_delivery("nonexist") is None

def test_queue_size():
    app = "wq3"
    clear_queue(app)
    enqueue_delivery(app_id=app, event_type="a", url="u", payload={})
    enqueue_delivery(app_id=app, event_type="b", url="u", payload={})
    assert get_queue_size(app) == 2

def test_clear():
    app = "wq4"
    enqueue_delivery(app_id=app, event_type="x", url="u", payload={})
    count = clear_queue(app)
    assert count >= 1
    assert get_queue_size(app) == 0
