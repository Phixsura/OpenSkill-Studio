import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_feedback import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback, Feedback,
)

class TestConsumerApiFeedback:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_submit_and_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback()
        svc.submit("inst-1", Feedback(feedback_id="f1", consumer_id="c1", rating=5, category="api_quality", comment="Great!", created_at=self._now()))
        svc.submit("inst-1", Feedback(feedback_id="f2", consumer_id="c1", rating=3, category="documentation", created_at=self._now()))
        summary = svc.get_summary("inst-1")
        assert summary.total_count == 2 and summary.average_rating == 4.0

    def test_invalid_rating(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback()
        with pytest.raises(ValueError, match="rating must be"):
            svc.submit("inst-1", Feedback(feedback_id="f1", consumer_id="c1", rating=6, category="general"))

    def test_update_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback()
        svc.submit("inst-1", Feedback(feedback_id="f1", consumer_id="c1", rating=4, category="support", created_at=self._now()))
        svc.update_status("inst-1", "f1", "resolved")
        items = svc.list_feedback("inst-1", status="resolved")
        assert len(items) == 1

    def test_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback()
        svc.submit("inst-1", Feedback(feedback_id="f1", consumer_id="c1", rating=5, category="performance", created_at=self._now()))
        summary = svc.get_summary("inst-1")
        assert summary.by_category["performance"] == 5.0

    def test_invalid_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback()
        with pytest.raises(ValueError, match="Invalid category"):
            svc.submit("inst-1", Feedback(feedback_id="f1", consumer_id="c1", rating=3, category="unknown"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback()
        svc.submit("inst-1", Feedback(feedback_id="f1", consumer_id="c1", rating=5, category="general", created_at=self._now()))
        assert svc.get_summary("inst-2").total_count == 0
