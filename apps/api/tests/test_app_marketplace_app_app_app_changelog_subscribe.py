from app.services.app_marketplace_app_app_app_changelog_subscribe import subscribe_to_changelog, build_subscriber_stats

def test_subscribe():
    r = subscribe_to_changelog(app_id="a1", email="alice@example.com", channels=["email", "slack"])
    assert r["subscription_id"].startswith("csub_")
    assert r["channels"] == ["email", "slack"]

def test_invalid_email():
    r = subscribe_to_changelog(app_id="a1", email="bad")
    assert "error" in r

def test_stats():
    subs = [
        {"status": "active", "channels": ["email", "slack"]},
        {"status": "active", "channels": ["email"]},
    ]
    r = build_subscriber_stats(subscriptions=subs)
    assert r["active"] == 2
    assert r["by_channel"]["email"] == 2
    assert r["by_channel"]["slack"] == 1
