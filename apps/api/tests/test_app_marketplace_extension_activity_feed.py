from app.services.app_marketplace_extension_activity_feed import ExtensionActivityFeedService


def test_record_and_feed():
    svc = ExtensionActivityFeedService()
    svc.record("ext-1", "install", "user-1", "Installed Slack Bot")
    svc.record("ext-1", "deploy", "admin", "Deployed v2.0")
    feed = svc.get_feed("ext-1")
    assert len(feed) == 2


def test_filter_by_type():
    svc = ExtensionActivityFeedService()
    svc.record("ext-1", "install", "u1", "install")
    svc.record("ext-1", "review", "u2", "review")
    svc.record("ext-1", "install", "u3", "install")
    feed = svc.get_feed(event_type="install")
    assert len(feed) == 2


def test_actor_activity():
    svc = ExtensionActivityFeedService()
    svc.record("ext-1", "install", "alice", "installed")
    svc.record("ext-2", "review", "alice", "reviewed")
    svc.record("ext-1", "deploy", "bob", "deployed")
    activity = svc.get_actor_activity("alice")
    assert len(activity) == 2


def test_recent_types():
    svc = ExtensionActivityFeedService()
    svc.record("ext-1", "install", "u1", "m")
    svc.record("ext-1", "install", "u2", "m")
    svc.record("ext-1", "deploy", "admin", "m")
    types = svc.get_recent_types("ext-1")
    assert types["install"] == 2
    assert types["deploy"] == 1


def test_active_extensions():
    svc = ExtensionActivityFeedService()
    for _ in range(10):
        svc.record("ext-hot", "install", "u", "m")
    for _ in range(3):
        svc.record("ext-cold", "install", "u", "m")
    active = svc.get_active_extensions(1)
    assert active[0]["extension_id"] == "ext-hot"
