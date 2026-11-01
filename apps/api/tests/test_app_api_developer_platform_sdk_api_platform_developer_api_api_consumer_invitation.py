import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_invitation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitation, InviteStatus,
)

class TestConsumerInvitation:
    def test_create_and_accept(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitation()
        inv = svc.create_invite("inst-1", "i1", "dev@example.com")
        accepted = svc.accept("inst-1", "i1", inv.token)
        assert accepted.status == InviteStatus.ACCEPTED

    def test_wrong_token(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitation()
        svc.create_invite("inst-1", "i1", "dev@example.com")
        with pytest.raises(ValueError, match="Invalid token"):
            svc.accept("inst-1", "i1", "wrong-token")

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitation()
        svc.create_invite("inst-1", "i1", "dev@example.com")
        inv = svc.revoke("inst-1", "i1")
        assert inv.status == InviteStatus.REVOKED

    def test_duplicate_email(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitation()
        svc.create_invite("inst-1", "i1", "dev@example.com")
        with pytest.raises(ValueError, match="already exists"):
            svc.create_invite("inst-1", "i2", "dev@example.com")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitation()
        svc.create_invite("inst-1", "i1", "dev@example.com")
        assert len(svc.pending_invites("inst-2")) == 0
