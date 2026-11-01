import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_token_rotation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotation,
)

class TestConsumerApiTokenRotation:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_issue_and_validate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotation()
        raw, token = svc.issue("inst-1", "c1", now=self._now())
        import hashlib
        found = svc.validate("inst-1", hashlib.sha256(raw.encode()).hexdigest(), now=self._now())
        assert found is not None and found.token_id == token.token_id

    def test_rotate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotation()
        _, old = svc.issue("inst-1", "c1", now=self._now())
        result = svc.rotate("inst-1", "c1", old.token_id, now=self._now())
        assert result.old_token_id == old.token_id and result.new_token_id != old.token_id

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotation()
        raw, token = svc.issue("inst-1", "c1", now=self._now())
        svc.revoke("inst-1", token.token_id)
        import hashlib
        assert svc.validate("inst-1", hashlib.sha256(raw.encode()).hexdigest(), now=self._now()) is None

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotation()
        raw, _ = svc.issue("inst-1", "c1", ttl_days=1, now=self._now())
        import hashlib
        assert svc.validate("inst-1", hashlib.sha256(raw.encode()).hexdigest(), now=self._now() + timedelta(days=2)) is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotation()
        raw, _ = svc.issue("inst-1", "c1", now=self._now())
        import hashlib
        assert svc.validate("inst-2", hashlib.sha256(raw.encode()).hexdigest(), now=self._now()) is None
