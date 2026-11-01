from app.services.app_marketplace_app_webhook_event_builder import build_event, validate_event_payload, serialize_event

def test_build():
    e = build_event(event_type="app.installed", app_id="a1", data={"org_id": "o1"})
    assert e["id"].startswith("evt_")
    assert e["event"] == "app.installed"

def test_validate_ok():
    e = {"event": "x", "app_id": "a1", "data": {}, "timestamp": 123}
    r = validate_event_payload(event=e)
    assert r["valid"]

def test_validate_missing():
    r = validate_event_payload(event={"event": "x"})
    assert not r["valid"]

def test_serialize():
    e = {"event": "test", "data": {"k": "v"}}
    s = serialize_event(event=e)
    assert '"event"' in s
