import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_consumer_lifecycle import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle, ConsumerAccount,
)

class TestConsumerLifecycle:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_activate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle()
        svc.create("inst-1", ConsumerAccount(consumer_id="c1", name="Acme Corp", created_at=self._now()))
        svc.transition("inst-1", "c1", "active", now=self._now())
        account = svc.get("inst-1", "c1")
        assert account.status == "active" and account.activated_at is not None

    def test_suspend_with_reason(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle()
        svc.create("inst-1", ConsumerAccount(consumer_id="c1", name="X", created_at=self._now()))
        svc.transition("inst-1", "c1", "active", now=self._now())
        svc.transition("inst-1", "c1", "suspended", reason="TOS violation", now=self._now())
        account = svc.get("inst-1", "c1")
        assert account.status == "suspended" and account.suspension_reason == "TOS violation"

    def test_invalid_transition(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle()
        svc.create("inst-1", ConsumerAccount(consumer_id="c1", name="X", created_at=self._now()))
        with pytest.raises(ValueError, match="Cannot transition"):
            svc.transition("inst-1", "c1", "suspended")  # pending -> suspended not allowed

    def test_reactivate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle()
        svc.create("inst-1", ConsumerAccount(consumer_id="c1", name="X", created_at=self._now()))
        svc.transition("inst-1", "c1", "active", now=self._now())
        svc.transition("inst-1", "c1", "suspended", now=self._now())
        svc.transition("inst-1", "c1", "active", now=self._now())
        assert svc.get("inst-1", "c1").status == "active"

    def test_list_by_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle()
        svc.create("inst-1", ConsumerAccount(consumer_id="c1", name="A", created_at=self._now()))
        svc.create("inst-1", ConsumerAccount(consumer_id="c2", name="B", created_at=self._now()))
        svc.transition("inst-1", "c1", "active", now=self._now())
        assert len(svc.list_by_status("inst-1", status="active")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiConsumerLifecycle()
        svc.create("inst-1", ConsumerAccount(consumer_id="c1", name="X", created_at=self._now()))
        assert svc.get("inst-2", "c1") is None
