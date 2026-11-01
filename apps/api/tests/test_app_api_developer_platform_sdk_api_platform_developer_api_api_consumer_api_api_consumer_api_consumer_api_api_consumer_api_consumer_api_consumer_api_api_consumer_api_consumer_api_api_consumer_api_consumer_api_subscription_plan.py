import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_subscription_plan import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan, SubscriptionPlan,
)

class TestSubscriptionPlan:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_subscribe(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan()
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="pro", name="Pro", price_cents_monthly=4999, features=["webhooks", "analytics"], request_limit=100000, rate_limit_rps=100))
        sub = svc.subscribe("inst-1", "c1", "pro", self._now())
        assert sub.status == "active" and sub.plan_id == "pro"

    def test_trial(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan()
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="pro", name="Pro", price_cents_monthly=4999))
        sub = svc.subscribe("inst-1", "c1", "pro", self._now(), trial_days=14)
        assert sub.status == "trialing" and sub.trial_ends_at is not None

    def test_cancel(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan()
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="pro", name="Pro", price_cents_monthly=4999))
        svc.subscribe("inst-1", "c1", "pro", self._now())
        sub = svc.cancel("inst-1", "c1", self._now())
        assert sub.status == "cancelled" and sub.ends_at is not None

    def test_upgrade(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan()
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="basic", name="Basic", price_cents_monthly=999))
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="pro", name="Pro", price_cents_monthly=4999))
        svc.subscribe("inst-1", "c1", "basic", self._now())
        sub = svc.upgrade("inst-1", "c1", "pro")
        assert sub.plan_id == "pro"

    def test_list_plans_sorted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan()
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="pro", name="Pro", price_cents_monthly=4999))
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="free", name="Free", price_cents_monthly=0))
        plans = svc.list_plans("inst-1")
        assert plans[0].name == "Free"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan()
        svc.create_plan("inst-1", SubscriptionPlan(plan_id="x", name="X", price_cents_monthly=100))
        assert len(svc.list_plans("inst-2")) == 0
