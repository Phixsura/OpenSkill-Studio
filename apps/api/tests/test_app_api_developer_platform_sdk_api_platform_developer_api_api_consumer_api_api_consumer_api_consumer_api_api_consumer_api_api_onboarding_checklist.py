import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_onboarding_checklist import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist, ChecklistItem,
)

class TestConsumerApiOnboardingChecklist:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist()
        items = [ChecklistItem(item_id="i1", title="Create API Key", required=True), ChecklistItem(item_id="i2", title="Set Webhook", required=True)]
        svc.create("inst-1", "c1", items, now=self._now())
        progress = svc.get_progress("inst-1", "c1")
        assert progress.total == 2 and progress.completed == 0 and not progress.fully_onboarded

    def test_complete_item(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist()
        svc.create("inst-1", "c1", [ChecklistItem(item_id="i1", title="Key", required=True)], now=self._now())
        svc.complete_item("inst-1", "c1", "i1", now=self._now())
        progress = svc.get_progress("inst-1", "c1")
        assert progress.completed == 1 and progress.fully_onboarded

    def test_partial_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist()
        svc.create("inst-1", "c1", [ChecklistItem(item_id="i1", title="A", required=True), ChecklistItem(item_id="i2", title="B", required=True), ChecklistItem(item_id="i3", title="C", required=False)], now=self._now())
        svc.complete_item("inst-1", "c1", "i1", now=self._now())
        progress = svc.get_progress("inst-1", "c1")
        assert progress.progress_pct == pytest.approx(33.3, abs=0.1) and not progress.fully_onboarded

    def test_optional_not_blocking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist()
        svc.create("inst-1", "c1", [ChecklistItem(item_id="i1", title="Required", required=True), ChecklistItem(item_id="i2", title="Optional", required=False)], now=self._now())
        svc.complete_item("inst-1", "c1", "i1", now=self._now())
        assert svc.get_progress("inst-1", "c1").fully_onboarded

    def test_empty_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist()
        with pytest.raises(ValueError, match="At least one"):
            svc.create("inst-1", "c1", [], now=self._now())

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist()
        svc.create("inst-1", "c1", [ChecklistItem(item_id="i1", title="X")], now=self._now())
        assert svc.get_checklist("inst-2", "c1") is None
