from app.services.app_marketplace_app_session_replay import create_session_recording, get_session_insights

def test_create():
    events = [{"type": "click", "duration_ms": 5000}, {"type": "error", "duration_ms": 1000},
              {"type": "scroll", "duration_ms": 3000}]
    r = create_session_recording(app_id="a1", user_id="u1", page_url="/dashboard", events=events)
    assert r["recording_id"].startswith("rec_")
    assert r["event_count"] == 3
    assert r["has_errors"]
    assert r["duration_ms"] == 9000

def test_insights():
    recs = [
        {"has_errors": True, "has_rage_clicks": False, "duration_ms": 10000},
        {"has_errors": False, "has_rage_clicks": True, "duration_ms": 5000},
        {"has_errors": False, "has_rage_clicks": False, "duration_ms": 8000},
    ]
    r = get_session_insights(recordings=recs)
    assert r["total_recordings"] == 3
    assert r["with_errors"] == 1
    assert r["with_rage_clicks"] == 1
    assert r["frustration_score"] > 0
