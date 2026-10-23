from app.services.app_marketplace_event_stream import create_event, filter_events, get_event_type_stats

def test_create():
    r = create_event(event_type="app.installed", source="marketplace", payload={"app_id": "a1"})
    assert r["event_id"].startswith("evt_")
    assert r["type"] == "app.installed"

def test_create_invalid():
    r = create_event(event_type="invalid.type", source="x", payload={})
    assert "error" in r

def test_filter():
    events = [{"type": "app.installed", "source": "web"}, {"type": "review.created", "source": "api"},
              {"type": "app.installed", "source": "api"}]
    r = filter_events(events=events, event_types=["app.installed"])
    assert r["total"] == 2

def test_stats():
    events = [{"type": "app.installed"}, {"type": "app.installed"}, {"type": "review.created"}]
    r = get_event_type_stats(events=events)
    assert r["unique_types"] == 2
    assert r["types"][0]["type"] == "app.installed"
