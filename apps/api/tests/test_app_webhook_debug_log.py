from app.services.app_webhook_debug_log import format_debug_entry, format_debug_log

def test_entry():
    e = format_debug_entry({"event_type": "app.installed", "url": "u", "http_status": 200, "status": "delivered", "duration_ms": 50})
    assert e["success"] is True
    assert e["method"] == "POST"

def test_log():
    log = format_debug_log([{"event_type": "a"}, {"event_type": "b"}])
    assert len(log) == 2
