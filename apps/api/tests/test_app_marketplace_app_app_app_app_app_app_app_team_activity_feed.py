from app.services.app_marketplace_app_app_app_app_app_app_app_team_activity_feed import build_activity_feed

def test_feed():
    events = [
        {"user": "alice", "type": "commit", "message": "feat: add auth", "timestamp": "2026-10-24T10:00:00Z"},
        {"user": "bob", "type": "review", "message": "LGTM on PR #51", "timestamp": "2026-10-24T11:00:00Z"},
        {"user": "alice", "type": "deploy", "message": "Deploy v3.1", "timestamp": "2026-10-24T12:00:00Z"},
    ]
    r = build_activity_feed(events)
    assert r["total"] == 3
    assert r["shown"] == 3
    assert r["items"][0]["timestamp"] == "2026-10-24T12:00:00Z"
    assert r["top_contributor"] == "alice"
    assert r["by_type"]["commit"] == 1
    assert r["items"][0]["icon"] == "🚀"

def test_filter():
    events = [
        {"user": "a", "type": "commit", "message": "x", "timestamp": "1"},
        {"user": "b", "type": "review", "message": "y", "timestamp": "2"},
    ]
    r = build_activity_feed(events, filter_type="commit")
    assert r["total"] == 1
    assert r["items"][0]["type"] == "commit"
