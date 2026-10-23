from app.services.app_marketplace_developer_event_log import log_event, query_events, compute_activity_stats

def test_log():
    e = log_event(category="app", event_type="app.created", actor_id="u1", app_id="a1")
    assert e["category"] == "app"

def test_query_category():
    events = [{"category": "app", "timestamp": "2026-01-01", "actor_id": "u1"},
              {"category": "webhook", "timestamp": "2026-01-02", "actor_id": "u1"}]
    r = query_events(events=events, category="app")
    assert len(r) == 1

def test_query_actor():
    events = [{"category": "app", "timestamp": "2026-01-01", "actor_id": "u1"},
              {"category": "app", "timestamp": "2026-01-02", "actor_id": "u2"}]
    r = query_events(events=events, actor_id="u1")
    assert len(r) == 1

def test_stats():
    events = [{"category": "app", "actor_id": "u1"}, {"category": "app", "actor_id": "u1"},
              {"category": "webhook", "actor_id": "u2"}]
    s = compute_activity_stats(events=events)
    assert s["total"] == 3
    assert s["unique_actors"] == 2
    assert s["top_actors"][0]["id"] == "u1"
