import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_session_tracker import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTracker, ConsumerSession,
)

class TestConsumerSessionTracker:
    def test_start_and_activity(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTracker()
        svc.start_session("inst-1", ConsumerSession(session_id="s1", consumer_id="c1"))
        s = svc.record_activity("inst-1", "s1")
        assert s.request_count == 1

    def test_end_session(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTracker()
        svc.start_session("inst-1", ConsumerSession(session_id="s1", consumer_id="c1"))
        assert svc.end_session("inst-1", "s1") is True
        assert svc.concurrent_count("inst-1") == 0

    def test_duplicate_session(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTracker()
        svc.start_session("inst-1", ConsumerSession(session_id="s1", consumer_id="c1"))
        with pytest.raises(ValueError, match="already exists"):
            svc.start_session("inst-1", ConsumerSession(session_id="s1", consumer_id="c1"))

    def test_unique_consumers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTracker()
        svc.start_session("inst-1", ConsumerSession(session_id="s1", consumer_id="c1"))
        svc.start_session("inst-1", ConsumerSession(session_id="s2", consumer_id="c2"))
        svc.start_session("inst-1", ConsumerSession(session_id="s3", consumer_id="c1"))
        assert svc.unique_consumers("inst-1") == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTracker()
        svc.start_session("inst-1", ConsumerSession(session_id="s1", consumer_id="c1"))
        assert svc.concurrent_count("inst-2") == 0
