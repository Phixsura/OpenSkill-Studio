import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_onboarding_checklist import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklist

STEPS = [{"step_id": "s1", "title": "Create API key", "required": True}, {"step_id": "s2", "title": "Set webhook URL", "required": True}, {"step_id": "s3", "title": "Read docs", "required": False}]

class TestOnboardingChecklist:
    def test_create_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklist()
        cl = svc.create_checklist("inst-1", "c1", STEPS)
        assert cl.progress_pct == 0.0
        assert len(cl.pending_steps) == 3

    def test_complete_steps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklist()
        svc.create_checklist("inst-1", "c1", STEPS)
        svc.complete_step("inst-1", "c1", "s1")
        svc.complete_step("inst-1", "c1", "s2")
        assert svc.is_onboarded("inst-1", "c1") is True
        cl = svc.get_checklist("inst-1", "c1")
        assert len(cl.pending_steps) == 1  # s3 optional, not completed

    def test_not_onboarded_without_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklist()
        svc.create_checklist("inst-1", "c1", STEPS)
        svc.complete_step("inst-1", "c1", "s3")  # only optional
        assert svc.is_onboarded("inst-1", "c1") is False

    def test_duplicate_checklist(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklist()
        svc.create_checklist("inst-1", "c1", STEPS)
        with pytest.raises(ValueError, match="already exists"):
            svc.create_checklist("inst-1", "c1", STEPS)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklist()
        svc.create_checklist("inst-1", "c1", STEPS)
        assert len(svc.list_checklists("inst-2")) == 0
