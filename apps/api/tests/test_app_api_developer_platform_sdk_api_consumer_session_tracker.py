from app.services.app_api_developer_platform_sdk_api_consumer_session_tracker import AppAPIDeveloperPlatformSDKApiConsumerSessionTracker

class TestConsumerSessionTracker:
    def test_start(self):
        t = AppAPIDeveloperPlatformSDKApiConsumerSessionTracker()
        s = t.start("inst-1", "s1", "c1")
        assert s.active is True
        assert s.request_count == 0

    def test_activity(self):
        t = AppAPIDeveloperPlatformSDKApiConsumerSessionTracker()
        t.start("inst-1", "s1", "c1")
        s = t.activity("inst-1", "s1", "/api/users")
        assert s.request_count == 1
        assert "/api/users" in s.endpoints_accessed

    def test_end(self):
        t = AppAPIDeveloperPlatformSDKApiConsumerSessionTracker()
        t.start("inst-1", "s1", "c1")
        s = t.end("inst-1", "s1")
        assert s.active is False

    def test_active_count(self):
        t = AppAPIDeveloperPlatformSDKApiConsumerSessionTracker()
        t.start("inst-1", "s1", "c1")
        t.start("inst-1", "s2", "c2")
        t.end("inst-1", "s1")
        assert t.active_count("inst-1") == 1

    def test_by_consumer(self):
        t = AppAPIDeveloperPlatformSDKApiConsumerSessionTracker()
        t.start("inst-1", "s1", "c1")
        t.start("inst-1", "s2", "c1")
        t.start("inst-1", "s3", "c2")
        assert len(t.by_consumer("inst-1", "c1")) == 2

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKApiConsumerSessionTracker()
        t.start("inst-1", "s1", "c1")
        assert t.active_count("inst-2") == 0
