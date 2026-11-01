from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_pub import publish_changelog, schedule_publish

def test_publish():
    r = publish_changelog("3.0", "Major update", ["New UI", "API v3"], ["email", "slack"])
    assert r["published"]
    assert r["channels_delivered"] == 2

def test_invalid():
    r = publish_changelog("1.0", "x", [], ["telegram"])
    assert not r["published"]

def test_schedule():
    import time
    r = schedule_publish("4.0", time.time() + 3600, ["email"])
    assert r["scheduled"]
    assert r["delay_sec"] > 0
