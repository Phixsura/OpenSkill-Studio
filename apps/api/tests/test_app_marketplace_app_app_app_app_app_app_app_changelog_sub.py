from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_sub import (
    subscribe, unsubscribe, subscriber_stats, clear_subs,
)

def test_subscribe():
    clear_subs()
    r = subscribe("u1", "email", "weekly")
    assert r["subscribed"]
    r2 = subscribe("u2", "slack", "immediate")
    assert r2["subscribed"]
    s = subscriber_stats()
    assert s["active"] == 2
    assert s["by_channel"]["email"] == 1
    unsubscribe("u1")
    assert subscriber_stats()["active"] == 1
    clear_subs()

def test_invalid():
    r = subscribe("u1", "sms")
    assert not r["subscribed"]
