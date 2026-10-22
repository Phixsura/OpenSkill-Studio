from app.services.app_webhook_inspector import inspect_delivery

def test_inspect():
    d = inspect_delivery({"id": "d1", "event_type": "app.installed", "url": "https://x.com",
        "status": "delivered", "http_status": 200, "duration_ms": 150, "created_at": "t1", "delivered_at": "t2"})
    assert d["status"] == "delivered"
    assert len(d["timeline"]) >= 2

def test_failed():
    d = inspect_delivery({"id": "d2", "status": "failed", "error": "timeout", "created_at": "t1", "failed_at": "t2"})
    assert d["error"] == "timeout"
    assert any(e["event"] == "failed" for e in d["timeline"])

def test_payload_size():
    d = inspect_delivery({"id": "d3", "payload": {"data": "x" * 100}})
    assert d["payload_size"] > 0
