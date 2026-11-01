import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_overview import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview, ConsumerOverview, OverviewMetric,
)

class TestConsumerApiOverview:
    def test_update_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview()
        svc.update("inst-1", ConsumerOverview(consumer_id="c1", plan="pro", status="active", health_score=95, active_keys=3, active_webhooks=2, team_members=5, metrics=[OverviewMetric(name="requests", value=10000, unit="req/day", trend="up", change_pct=15)]))
        overview = svc.get("inst-1", "c1")
        assert overview.plan == "pro" and overview.health_score == 95

    def test_list_sorted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview()
        svc.update("inst-1", ConsumerOverview(consumer_id="c1", plan="free", status="active", health_score=60))
        svc.update("inst-1", ConsumerOverview(consumer_id="c2", plan="pro", status="active", health_score=95))
        lst = svc.list_all("inst-1")
        assert lst[0].consumer_id == "c2"

    def test_filter_by_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview()
        svc.update("inst-1", ConsumerOverview(consumer_id="c1", plan="free", status="active"))
        svc.update("inst-1", ConsumerOverview(consumer_id="c2", plan="free", status="suspended"))
        assert len(svc.list_all("inst-1", status="active")) == 1

    def test_platform_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview()
        svc.update("inst-1", ConsumerOverview(consumer_id="c1", plan="pro", status="active", health_score=90, active_keys=5))
        svc.update("inst-1", ConsumerOverview(consumer_id="c2", plan="free", status="active", health_score=80, active_keys=2))
        summary = svc.get_platform_summary("inst-1")
        assert summary["total_consumers"] == 2 and summary["total_keys"] == 7

    def test_invalid_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview()
        with pytest.raises(ValueError, match="Invalid status"):
            svc.update("inst-1", ConsumerOverview(consumer_id="c1", plan="x", status="banned"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview()
        svc.update("inst-1", ConsumerOverview(consumer_id="c1", plan="pro", status="active"))
        assert svc.get("inst-2", "c1") is None
