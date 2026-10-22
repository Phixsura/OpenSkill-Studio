from app.services.app_event_log_formatter import format_event_log_entry, format_event_log, summarize_event_log

def test_format_entry():
    e = format_event_log_entry({"event_id": "e1", "event_type": "app.installed", "org_id": "org-123", "delivered": True})
    assert e["status"] == "delivered"
    assert "app.installed" in e["display"]

def test_format_log():
    events = [{"event_type": "a"}, {"event_type": "b"}]
    assert len(format_event_log(events)) == 2

def test_summarize():
    events = [{"event_type": "a"}, {"event_type": "a"}, {"event_type": "b"}]
    s = summarize_event_log(events)
    assert s["total"] == 3
    assert s["unique_types"] == 2
    assert s["by_type"]["a"] == 2
