import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_consumer_api_api_consumer_api_api_consumer_api_api_consumer_api_getting_started import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted, GettingStartedStep,
)

class TestGettingStarted:
    def _now(self):
        return datetime(2026, 6, 1)

    def _steps(self):
        return [
            GettingStartedStep(step_id="s1", title="Create API Key", description="Generate your first API key", order=1),
            GettingStartedStep(step_id="s2", title="Make First Request", description="Call GET /api/users", code_snippet="curl -H 'Authorization: Bearer KEY' https://api.example.com/v1/users", order=2),
            GettingStartedStep(step_id="s3", title="Set Up Webhook", description="Configure a webhook endpoint", order=3),
        ]

    def test_initialize_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted()
        svc.initialize("inst-1", "c1", self._steps(), now=self._now())
        progress = svc.get_progress("inst-1", "c1")
        assert progress["total"] == 3 and progress["completed"] == 0 and not progress["done"]

    def test_complete_steps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted()
        svc.initialize("inst-1", "c1", self._steps(), now=self._now())
        svc.complete_step("inst-1", "c1", "s1", now=self._now())
        svc.complete_step("inst-1", "c1", "s2", now=self._now())
        svc.complete_step("inst-1", "c1", "s3", now=self._now())
        progress = svc.get_progress("inst-1", "c1")
        assert progress["done"] and progress["pct"] == 100

    def test_next_step(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted()
        svc.initialize("inst-1", "c1", self._steps(), now=self._now())
        svc.complete_step("inst-1", "c1", "s1", now=self._now())
        next_step = svc.get_next_step("inst-1", "c1")
        assert next_step.step_id == "s2"

    def test_empty_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted()
        with pytest.raises(ValueError, match="At least one"):
            svc.initialize("inst-1", "c1", [], now=self._now())

    def test_all_done_returns_none(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted()
        svc.initialize("inst-1", "c1", [GettingStartedStep(step_id="s1", title="X", description="Y")], now=self._now())
        svc.complete_step("inst-1", "c1", "s1", now=self._now())
        assert svc.get_next_step("inst-1", "c1") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStarted()
        svc.initialize("inst-1", "c1", self._steps(), now=self._now())
        assert svc.get_guide("inst-2", "c1") is None
