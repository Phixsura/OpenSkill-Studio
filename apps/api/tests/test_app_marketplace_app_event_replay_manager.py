from app.services.app_marketplace_app_event_replay_manager import create_replay_job, execute_replay, build_replay_summary

def test_create():
    j = create_replay_job(app_id="a1", event_ids=["e1", "e2"], target_url="https://x.com/hook")
    assert j["event_count"] == 2
    assert j["status"] == "queued"

def test_empty():
    j = create_replay_job(app_id="a1", event_ids=[], target_url="https://x.com")
    assert j["error"]

def test_too_many():
    j = create_replay_job(app_id="a1", event_ids=[f"e{i}" for i in range(200)], target_url="https://x.com")
    assert j["error"]

def test_execute():
    r = execute_replay(events=[{"id": "e1"}, {"id": "e2"}])
    assert r["delivered"] == 2

def test_summary():
    s = build_replay_summary(job={"app_id": "a1"}, results={"total": 10, "delivered": 9})
    assert s["success_rate"] == 90.0
