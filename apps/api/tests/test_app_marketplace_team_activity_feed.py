from app.services.app_marketplace_team_activity_feed import build_activity_feed, get_activity_stats

def test_feed():
    r = build_activity_feed(team_id="t1")
    assert r["total"] == 5
    assert r["activities"][0]["actor"] == "Alice"
    assert r["activities"][0]["action"] == "published"

def test_limit():
    r = build_activity_feed(team_id="t1", limit=2)
    assert len(r["activities"]) == 2
    assert r["has_more"]

def test_stats():
    r = get_activity_stats(team_id="t1")
    assert r["active_members"] == 4
    assert r["today"]["commits"] == 12
