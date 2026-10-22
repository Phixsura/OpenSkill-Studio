from app.services.app_webhook_event_catalog import get_catalog, search_catalog, get_all_events

def test_catalog():
    c = get_catalog()
    assert "submission" in c
    assert "app" in c

def test_search():
    r = search_catalog("graded")
    assert len(r) == 1
    assert r[0]["event"] == "submission.graded"

def test_search_empty():
    assert search_catalog("nonexistent") == []

def test_all_events():
    events = get_all_events()
    assert "app.installed" in events
    assert len(events) >= 7
