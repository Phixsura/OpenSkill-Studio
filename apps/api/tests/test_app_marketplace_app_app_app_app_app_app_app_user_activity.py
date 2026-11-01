from app.services.app_marketplace_app_app_app_app_app_app_app_user_activity import UserActivityLog

def test_activity():
    log = UserActivityLog()
    log.record(user_id="alice", action="create", resource="app/myapp")
    log.record(user_id="alice", action="deploy", resource="app/myapp")
    log.record(user_id="bob", action="login", resource="session")
    feed = log.get_feed("alice")
    assert len(feed) == 2
    assert feed[0]["action"] == "deploy"  # most recent first
    s = log.stats("alice")
    assert s["total_actions"] == 2
    assert s["by_action"]["create"] == 1
    recent = log.recent_activity()
    assert len(recent) == 3
