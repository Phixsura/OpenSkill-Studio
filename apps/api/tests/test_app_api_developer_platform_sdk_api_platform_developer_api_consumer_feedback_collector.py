import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_feedback_collector import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollector, FeedbackEntry,
)

class TestConsumerFeedbackCollector:
    def test_submit_and_average(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollector()
        svc.submit("inst-1", FeedbackEntry(feedback_id="f1", consumer_id="c1", endpoint="/api", rating=5, category="feature"))
        svc.submit("inst-1", FeedbackEntry(feedback_id="f2", consumer_id="c2", endpoint="/api", rating=3, category="bug"))
        assert svc.average_rating("inst-1") == 4.0

    def test_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollector()
        svc.submit("inst-1", FeedbackEntry(feedback_id="f1", consumer_id="c1", endpoint="/a", rating=4, category="bug"))
        svc.submit("inst-1", FeedbackEntry(feedback_id="f2", consumer_id="c1", endpoint="/a", rating=3, category="bug"))
        svc.submit("inst-1", FeedbackEntry(feedback_id="f3", consumer_id="c1", endpoint="/a", rating=5, category="feature"))
        cats = svc.by_category("inst-1")
        assert cats["bug"] == 2 and cats["feature"] == 1

    def test_low_rated(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollector()
        svc.submit("inst-1", FeedbackEntry(feedback_id="f1", consumer_id="c1", endpoint="/bad", rating=1, category="bug"))
        svc.submit("inst-1", FeedbackEntry(feedback_id="f2", consumer_id="c1", endpoint="/bad", rating=2, category="bug"))
        low = svc.low_rated_endpoints("inst-1", 3.0)
        assert len(low) == 1 and low[0][0] == "/bad"

    def test_invalid_rating(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollector()
        with pytest.raises(ValueError, match="Rating"):
            svc.submit("inst-1", FeedbackEntry(feedback_id="f1", consumer_id="c1", endpoint="/a", rating=6, category="bug"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollector()
        svc.submit("inst-1", FeedbackEntry(feedback_id="f1", consumer_id="c1", endpoint="/a", rating=5, category="other"))
        assert svc.count("inst-2") == 0
