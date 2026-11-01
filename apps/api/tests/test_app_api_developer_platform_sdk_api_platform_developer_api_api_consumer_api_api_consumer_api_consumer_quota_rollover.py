import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_quota_rollover import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRollover, QuotaPeriod, RolloverPolicy,
)

class TestConsumerQuotaRollover:
    def test_basic_rollover(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRollover()
        svc.create_period("inst-1", "c1", QuotaPeriod(period_id="jan", consumer_id="c1", base_quota=1000, used=800))
        svc.create_period("inst-1", "c1", QuotaPeriod(period_id="feb", consumer_id="c1", base_quota=1000))
        rolled = svc.rollover("inst-1", "c1", "jan", "feb")
        assert rolled == 200  # min(remaining=200, max=200 i.e. 20% of 1000)
        feb = svc.get_period("inst-1", "c1", "feb")
        assert feb.total_available == 1200

    def test_capped_by_policy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRollover()
        svc.set_policy("inst-1", "c1", RolloverPolicy(max_rollover_pct=0.1))
        svc.create_period("inst-1", "c1", QuotaPeriod(period_id="jan", consumer_id="c1", base_quota=1000, used=0))
        svc.create_period("inst-1", "c1", QuotaPeriod(period_id="feb", consumer_id="c1", base_quota=1000))
        rolled = svc.rollover("inst-1", "c1", "jan", "feb")
        assert rolled == 100  # 10% cap, even though 1000 remaining

    def test_use_quota(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRollover()
        svc.create_period("inst-1", "c1", QuotaPeriod(period_id="jan", consumer_id="c1", base_quota=100))
        svc.use_quota("inst-1", "c1", "jan", 60)
        p = svc.get_period("inst-1", "c1", "jan")
        assert p.remaining == 40

    def test_rolled_in_adds_to_available(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRollover()
        svc.create_period("inst-1", "c1", QuotaPeriod(period_id="feb", consumer_id="c1", base_quota=500, rolled_in=50))
        p = svc.get_period("inst-1", "c1", "feb")
        assert p.total_available == 550

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRollover()
        svc.create_period("inst-1", "c1", QuotaPeriod(period_id="jan", consumer_id="c1", base_quota=100))
        assert svc.get_period("inst-2", "c1", "jan") is None
