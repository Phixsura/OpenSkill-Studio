from app.services.app_marketplace_app_app_app_app_app_app_app_session_replay import SessionReplayRecorder

def test_replay():
    rec = SessionReplayRecorder()
    rec.start("s1", user_id="u1", page="/dashboard")
    rec.record_event("s1", event_type="click", target="button.save", timestamp_ms=1000)
    rec.record_event("s1", event_type="scroll", target="main", timestamp_ms=2000)
    rec.record_event("s1", event_type="error", target="api/users", timestamp_ms=3000)
    r = rec.get_replay("s1")
    assert r["total_events"] == 3
    assert r["error_count"] == 1
    assert r["has_errors"]
    assert r["duration_display"] == "3.0s"
    assert r["start_page"] == "/dashboard"

def test_not_found():
    rec = SessionReplayRecorder()
    assert "error" in rec.get_replay("nope")
