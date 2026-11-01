import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_rate_limit_exemption import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemption, RateLimitExemption,
)
import time

class TestConsumerApiRateLimitExemption:
    def test_grant_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemption()
        svc.grant("inst-1", RateLimitExemption(exemption_id="e1", consumer_id="c1", reason="Launch event", multiplier=3.0, expires_at=time.time() + 86400))
        assert svc.get_multiplier("inst-1", "c1") == 3.0

    def test_default_multiplier(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemption()
        assert svc.get_multiplier("inst-1", "c1") == 1.0

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemption()
        svc.grant("inst-1", RateLimitExemption(exemption_id="e1", consumer_id="c1", reason="Test", multiplier=2.0))
        svc.revoke("inst-1", "c1")
        assert svc.get_multiplier("inst-1", "c1") == 1.0

    def test_invalid_multiplier(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemption()
        with pytest.raises(ValueError, match="multiplier"):
            svc.grant("inst-1", RateLimitExemption(exemption_id="e1", consumer_id="c1", reason="X", multiplier=0.5))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemption()
        svc.grant("inst-1", RateLimitExemption(exemption_id="e1", consumer_id="c1", reason="X"))
        assert len(svc.list_exemptions("inst-2")) == 0
