from app.services.app_marketplace_app_audit_trail import create_audit_entry, query_audit_trail, summarize_audit

def test_create():
    e = create_audit_entry(app_id="a1", action="app.created", actor_id="u1", details={"name": "MyApp"})
    assert e["action"] == "app.created"
    assert e["error"] is None

def test_invalid_action():
    e = create_audit_entry(app_id="a1", action="invalid.action", actor_id="u1")
    assert e["error"]

def test_query_all():
    entries = [{"action": "app.created", "actor_id": "u1", "timestamp": "2026-01-01"},
               {"action": "version.submitted", "actor_id": "u2", "timestamp": "2026-01-02"}]
    r = query_audit_trail(entries=entries)
    assert r["filtered"] == 2
    assert r["entries"][0]["timestamp"] > r["entries"][1]["timestamp"]

def test_query_filter():
    entries = [{"action": "app.created", "actor_id": "u1", "timestamp": "2026-01-01"},
               {"action": "version.submitted", "actor_id": "u2", "timestamp": "2026-01-02"}]
    r = query_audit_trail(entries=entries, action_filter="app.created")
    assert r["filtered"] == 1

def test_summarize():
    entries = [{"action": "app.created", "actor_id": "u1"},
               {"action": "app.created", "actor_id": "u2"},
               {"action": "version.submitted", "actor_id": "u1"}]
    s = summarize_audit(entries=entries)
    assert s["total_events"] == 3
    assert s["unique_actors"] == 2
    assert s["top_actions"][0]["action"] == "app.created"
