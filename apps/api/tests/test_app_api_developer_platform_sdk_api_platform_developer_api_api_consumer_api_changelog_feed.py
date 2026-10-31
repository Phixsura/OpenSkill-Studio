from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_changelog_feed import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiChangelogFeed, ChangelogEntry,
)

class TestConsumerChangelogFeed:
    def test_publish_and_feed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiChangelogFeed()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="v2.0", title="New auth", change_type="feature", affected_endpoints=["/auth"]))
        feed = svc.feed_for_consumer("inst-1", "c1")
        assert len(feed) == 1 and feed[0].entry.title == "New auth"

    def test_relevance_filter(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiChangelogFeed()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="v2", title="Auth update", change_type="fix", affected_endpoints=["/auth"]))
        feed = svc.feed_for_consumer("inst-1", "c1", endpoints=["/orders"])
        assert feed[0].relevant is False

    def test_mark_read(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiChangelogFeed()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="v1", title="Fix", change_type="fix"))
        assert svc.unread_count("inst-1", "c1") == 1
        svc.mark_read("inst-1", "c1", "e1")
        assert svc.unread_count("inst-1", "c1") == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiChangelogFeed()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="v1", title="X", change_type="feature"))
        assert svc.entry_count("inst-2") == 0
