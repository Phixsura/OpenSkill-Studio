from app.services.app_marketplace_app_app_event_replay import create_replay, get_replay_progress

def test_create():
    r = create_replay(event_ids=["e1", "e2", "e3"], target_endpoint="https://x.com/hook", speed=2.0)
    assert r["replay_id"].startswith("rpl_")
    assert r["event_count"] == 3
    assert r["speed"] == 2.0

def test_empty():
    r = create_replay(event_ids=[], target_endpoint="x")
    assert "error" in r

def test_progress():
    r = get_replay_progress(total=10, delivered=7, failed=1)
    assert r["remaining"] == 2
    assert r["progress_pct"] == 70.0
    assert r["status"] == "in_progress"
