from app.services.app_marketplace_app_app_app_app_app_app_app_activity_feed import (
    add_activity, get_feed, clear_activities,
)

def test_feed():
    clear_activities()
    add_activity("alice", "deployed", "api-v2")
    add_activity("bob", "reviewed", "PR #42")
    add_activity("alice", "created", "webhook-config")
    r = get_feed()
    assert r["count"] == 3
    assert r["items"][0]["target"] == "webhook-config"  # most recent first
    r2 = get_feed(actor="alice")
    assert r2["count"] == 2
    clear_activities()

def test_escape():
    clear_activities()
    add_activity("<script>", "hacked", "db&server")
    r = get_feed()
    assert "<script>" not in r["items"][0]["actor"]
    clear_activities()
