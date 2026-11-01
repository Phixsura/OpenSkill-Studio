from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_replay_mgr import (
    create_replay, attempt_replay, replay_stats,
)

def test_replay():
    r = create_replay("wh1", "https://hook.com", '{"e":"test"}', 500, max_retries=2)
    assert r["status"] == "pending"
    a1 = attempt_replay(r, False)
    assert not a1["delivered"]
    a2 = attempt_replay(r, False)
    assert a2["exhausted"]
    assert r["status"] == "exhausted"

def test_success():
    r = create_replay("wh2", "https://a.com", "{}", 500)
    a = attempt_replay(r, True)
    assert a["delivered"]

def test_stats():
    replays = [{"status": "delivered"}, {"status": "delivered"}, {"status": "exhausted"}]
    s = replay_stats(replays)
    assert s["delivery_rate"] == 67
