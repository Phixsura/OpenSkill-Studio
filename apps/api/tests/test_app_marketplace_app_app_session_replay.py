from app.services.app_marketplace_app_app_session_replay import create_session_record, build_session_list

def test_create():
    r = create_session_record(user_id="u1", page_url="https://app.com/dash", duration_s=125, events=50, errors=2)
    assert r["session_id"].startswith("ses_")
    assert r["duration_display"] == "2m 5s"
    assert r["has_errors"]

def test_list():
    sessions = [
        {"duration_s": 60, "has_errors": False},
        {"duration_s": 120, "has_errors": True},
    ]
    r = build_session_list(sessions=sessions)
    assert r["total"] == 2
    assert r["avg_duration_s"] == 90
    assert r["error_sessions"] == 1
