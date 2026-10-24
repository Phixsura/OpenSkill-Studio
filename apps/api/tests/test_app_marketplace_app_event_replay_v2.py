from app.services.app_marketplace_app_event_replay_v2 import create_replay_v2, filter_events_for_replay, build_replay_preview

def test_create():
    r = create_replay_v2(app_id="a1", event_filter={"event_type": "install"}, target_url="https://x.com", dry_run=True)
    assert r["dry_run"]
    assert r["status"] == "queued"

def test_filter_type():
    events = [{"type": "install", "timestamp": "2026-01-01"}, {"type": "update", "timestamp": "2026-01-02"}]
    r = filter_events_for_replay(events=events, filter_config={"event_type": "install"})
    assert len(r) == 1

def test_filter_since():
    events = [{"type": "x", "timestamp": "2026-01-01"}, {"type": "x", "timestamp": "2026-06-01"}]
    r = filter_events_for_replay(events=events, filter_config={"since": "2026-03-01"})
    assert len(r) == 1

def test_filter_failed():
    events = [{"type": "x", "delivery_status": "failed"}, {"type": "x", "delivery_status": "success"}]
    r = filter_events_for_replay(events=events, filter_config={"status": "failed"})
    assert len(r) == 1

def test_preview():
    events = [{"type": "install"}, {"type": "install"}, {"type": "update"}]
    p = build_replay_preview(events=events, dry_run=True)
    assert p["event_count"] == 3
    assert p["by_type"]["install"] == 2
