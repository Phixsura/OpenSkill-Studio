from app.services.app_marketplace_app_changelog_subscription import subscribe_to_changelog, get_subscriber_count

def test_subscribe():
    r = subscribe_to_changelog(user_id="u1", app_id="a1", channels=["email", "push"])
    assert r["subscription_id"].startswith("clsub_")
    assert r["channels"] == ["email", "push"]

def test_invalid_channel():
    r = subscribe_to_changelog(user_id="u1", app_id="a1", channels=["sms"])
    assert "error" in r

def test_empty():
    r = subscribe_to_changelog(user_id="u1", app_id="a1", channels=[])
    assert "error" in r

def test_count():
    subs = [{"user_id": "u1", "channels": ["email"]}, {"user_id": "u2", "channels": ["email", "push"]}]
    r = get_subscriber_count(subscriptions=subs)
    assert r["total_subscribers"] == 2
    assert r["by_channel"]["email"] == 2
    assert r["by_channel"]["push"] == 1
