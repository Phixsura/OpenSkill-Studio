import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_key_expiration_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy, ExpirationPolicy,
)

class TestConsumerApiKeyExpirationPolicy:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_active_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy()
        svc.set_policy("inst-1", ExpirationPolicy(consumer_id="c1", max_lifetime_days=90, warn_before_days=14))
        svc.register_key("inst-1", "c1", "k1", self._now())
        check = svc.check("inst-1", "c1", "k1", self._now() + timedelta(days=10))
        assert check.status == "active" and not check.action_required

    def test_warning(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy()
        svc.set_policy("inst-1", ExpirationPolicy(consumer_id="c1", max_lifetime_days=90, warn_before_days=14))
        svc.register_key("inst-1", "c1", "k1", self._now())
        check = svc.check("inst-1", "c1", "k1", self._now() + timedelta(days=80))
        assert check.status == "warning" and check.days_remaining == 10

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy()
        svc.set_policy("inst-1", ExpirationPolicy(consumer_id="c1", max_lifetime_days=30))
        svc.register_key("inst-1", "c1", "k1", self._now())
        check = svc.check("inst-1", "c1", "k1", self._now() + timedelta(days=35))
        assert check.status == "expired"

    def test_list_expiring(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy()
        svc.set_policy("inst-1", ExpirationPolicy(consumer_id="c1", max_lifetime_days=30, warn_before_days=10))
        svc.register_key("inst-1", "c1", "k1", self._now())
        svc.register_key("inst-1", "c1", "k2", self._now() + timedelta(days=10))
        expiring = svc.list_expiring("inst-1", self._now() + timedelta(days=25))
        assert len(expiring) == 1 and expiring[0].key_id == "k1"

    def test_invalid_policy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy()
        with pytest.raises(ValueError, match="warn_before_days"):
            svc.set_policy("inst-1", ExpirationPolicy(consumer_id="c1", max_lifetime_days=30, warn_before_days=30))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy()
        svc.register_key("inst-1", "c1", "k1", self._now())
        with pytest.raises(ValueError):
            svc.check("inst-2", "c1", "k1", self._now())
