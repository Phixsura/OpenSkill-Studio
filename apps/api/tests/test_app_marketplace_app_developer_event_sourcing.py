from app.services.app_marketplace_app_developer_event_sourcing import append_event, replay_events, get_event_stream_info

def test_append():
    e = append_event(stream_id="app-1", event_type="created", data={"name": "App"}, version=1)
    assert e["version"] == 1

def test_replay():
    events = [
        {"event_type": "created", "data": {"name": "App", "status": "draft"}, "version": 1},
        {"event_type": "updated", "data": {"status": "published"}, "version": 2},
    ]
    r = replay_events(events=events)
    assert r["state"]["name"] == "App"
    assert r["state"]["status"] == "published"
    assert r["version"] == 2

def test_replay_delete():
    events = [
        {"event_type": "created", "data": {"name": "X"}, "version": 1},
        {"event_type": "deleted", "data": {}, "version": 2},
    ]
    r = replay_events(events=events)
    assert r["state"]["_deleted"]

def test_stream_info():
    events = [{"event_type": "created", "timestamp": "2026-01-01"},
              {"event_type": "updated", "timestamp": "2026-06-01"},
              {"event_type": "updated", "timestamp": "2026-07-01"}]
    r = get_event_stream_info(events=events)
    assert r["total_events"] == 3
    assert r["event_types"]["updated"] == 2
