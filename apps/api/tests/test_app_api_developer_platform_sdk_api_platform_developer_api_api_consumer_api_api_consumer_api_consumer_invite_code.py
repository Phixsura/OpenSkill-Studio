import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_invite_code import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode,
)

class TestConsumerInviteCode:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_generate_and_redeem(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode()
        invite = svc.generate("inst-1", "admin", plan_id="pro", now=self._now())
        assert len(invite.code) == 12
        result = svc.redeem("inst-1", invite.code, "consumer-1", now=self._now())
        assert result.success

    def test_max_uses(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode()
        invite = svc.generate("inst-1", "admin", max_uses=1, now=self._now())
        svc.redeem("inst-1", invite.code, "c1", now=self._now())
        result = svc.redeem("inst-1", invite.code, "c2", now=self._now())
        assert not result.success and result.reason == "max_uses_reached"

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode()
        invite = svc.generate("inst-1", "admin", ttl_days=1, now=self._now())
        result = svc.redeem("inst-1", invite.code, "c1", now=self._now() + timedelta(days=2))
        assert not result.success and result.reason == "code_expired"

    def test_duplicate_redemption(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode()
        invite = svc.generate("inst-1", "admin", max_uses=5, now=self._now())
        svc.redeem("inst-1", invite.code, "c1", now=self._now())
        result = svc.redeem("inst-1", invite.code, "c1", now=self._now())
        assert not result.success and result.reason == "already_redeemed"

    def test_disable(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode()
        invite = svc.generate("inst-1", "admin", now=self._now())
        svc.disable("inst-1", invite.code)
        result = svc.redeem("inst-1", invite.code, "c1", now=self._now())
        assert not result.success and result.reason == "code_disabled"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCode()
        invite = svc.generate("inst-1", "admin", now=self._now())
        result = svc.redeem("inst-2", invite.code, "c1", now=self._now())
        assert not result.success and result.reason == "code_not_found"
