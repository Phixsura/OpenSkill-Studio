import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_data_retention import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention, RetentionPolicy, RetentionRecord,
)

class TestConsumerApiDataRetention:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_set_and_get_policy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention()
        svc.set_policy("inst-1", "c1", RetentionPolicy(policy_id="p1", data_type="logs", retention_days=30))
        policies = svc.get_policies("inst-1", "c1")
        assert len(policies) == 1 and policies[0].retention_days == 30

    def test_check_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention()
        svc.set_policy("inst-1", "c1", RetentionPolicy(policy_id="p1", data_type="logs", retention_days=7))
        svc.record_data("inst-1", "c1", RetentionRecord(data_type="logs", record_count=1000, oldest_at=self._now() - timedelta(days=10), newest_at=self._now()))
        expired = svc.check_expired("inst-1", "c1", self._now())
        assert len(expired) == 1

    def test_not_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention()
        svc.set_policy("inst-1", "c1", RetentionPolicy(policy_id="p1", data_type="logs", retention_days=30))
        svc.record_data("inst-1", "c1", RetentionRecord(data_type="logs", record_count=100, oldest_at=self._now() - timedelta(days=5), newest_at=self._now()))
        assert len(svc.check_expired("inst-1", "c1", self._now())) == 0

    def test_purge(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention()
        svc.set_policy("inst-1", "c1", RetentionPolicy(policy_id="p1", data_type="logs", retention_days=7))
        svc.record_data("inst-1", "c1", RetentionRecord(data_type="logs", record_count=500, oldest_at=self._now() - timedelta(days=10), newest_at=self._now(), bytes_estimate=50000))
        result = svc.purge("inst-1", "c1", "logs", self._now())
        assert result.records_purged == 500 and result.archived

    def test_invalid_data_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention()
        with pytest.raises(ValueError, match="Invalid data_type"):
            svc.set_policy("inst-1", "c1", RetentionPolicy(policy_id="p1", data_type="unknown", retention_days=30))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention()
        svc.set_policy("inst-1", "c1", RetentionPolicy(policy_id="p1", data_type="logs", retention_days=30))
        assert len(svc.get_policies("inst-2", "c1")) == 0
