from app.services.app_marketplace_extension_changelog_feed import ChangelogFeedService

def test_publish_and_feed():
    svc = ChangelogFeedService()
    svc.publish("ext-1", "1.0.0", ["Initial release"], "feature")
    svc.publish("ext-1", "1.1.0", ["Bug fix"], "fix")
    assert len(svc.get_feed()) == 2

def test_filter_by_type():
    svc = ChangelogFeedService()
    svc.publish("ext-1", "2.0.0", ["Breaking API change"], "breaking")
    svc.publish("ext-1", "1.5.0", ["New widget"], "feature")
    assert len(svc.get_breaking_changes()) == 1
    assert svc.count_by_type()["breaking"] == 1

def test_filter_by_extension():
    svc = ChangelogFeedService()
    svc.publish("ext-1", "1.0.0", ["A"], "feature")
    svc.publish("ext-2", "1.0.0", ["B"], "feature")
    assert len(svc.get_feed(extension_id="ext-1")) == 1
