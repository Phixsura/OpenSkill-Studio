from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_quota_reset_scheduler import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetScheduler

class TestQuotaResetScheduler:
    def test_schedule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetScheduler()
        s = svc.schedule("inst-1", "c1", "daily")
        assert s.reset_interval == "daily"
        assert s.next_reset > s.last_reset

    def test_not_due_yet(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetScheduler()
        svc.schedule("inst-1", "c1", "daily")
        assert svc.check_and_reset("inst-1", "c1") is False  # just scheduled

    def test_due_for_reset(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetScheduler()
        svc.schedule("inst-1", "c1", "hourly")
        # Manually set next_reset to past
        sched = svc._schedules[("inst-1", "c1")]
        sched.next_reset = 0
        assert svc.check_and_reset("inst-1", "c1") is True
        assert sched.total_resets == 1

    def test_invalid_interval(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetScheduler()
        import pytest
        with pytest.raises(ValueError):
            svc.schedule("inst-1", "c1", "yearly")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiQuotaResetScheduler()
        svc.schedule("inst-1", "c1", "daily")
        assert len(svc.list_schedules("inst-2")) == 0
