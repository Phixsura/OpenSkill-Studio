from app.services.app_marketplace_app_app_playground_session import create_session, execute_code, list_sessions

def test_create():
    r = create_session(language="python", user_id="u1", timeout_s=120)
    assert r["session_id"].startswith("play_")
    assert r["status"] == "active"
    assert r["language"] == "python"

def test_execute():
    r = execute_code(session_id="play_abc", code="print('hello')\nprint('world')")
    assert r["status"] == "completed"
    assert r["line_count"] == 2

def test_list():
    sessions = [{"status": "active"}, {"status": "expired"}, {"status": "active"}]
    r = list_sessions(sessions=sessions)
    assert r["active"] == 2
    assert r["total"] == 3
