import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_onboarding_wizard import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiOnboardingWizard, OnboardingWizard, WizardStep,
)

STEPS = [WizardStep("s1", "Create Key", "Generate API key", 1), WizardStep("s2", "First Call", "Make first request", 2), WizardStep("s3", "Read Docs", "Optional", 3, skippable=True)]

class TestOnboardingWizard:
    def test_create_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiOnboardingWizard()
        w = svc.create_wizard("inst-1", OnboardingWizard(wizard_id="w1", consumer_id="c1", steps=list(STEPS)))
        assert w.progress_pct == 0.0

    def test_complete_required_steps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiOnboardingWizard()
        svc.create_wizard("inst-1", OnboardingWizard(wizard_id="w1", consumer_id="c1", steps=list(STEPS)))
        svc.complete_step("inst-1", "c1", "s1")
        svc.complete_step("inst-1", "c1", "s2")
        w = svc.get_wizard("inst-1", "c1")
        assert w.is_complete is True  # s3 is skippable

    def test_not_complete_without_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiOnboardingWizard()
        svc.create_wizard("inst-1", OnboardingWizard(wizard_id="w1", consumer_id="c1", steps=list(STEPS)))
        svc.complete_step("inst-1", "c1", "s3")  # only optional
        assert svc.get_wizard("inst-1", "c1").is_complete is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiOnboardingWizard()
        svc.create_wizard("inst-1", OnboardingWizard(wizard_id="w1", consumer_id="c1", steps=[WizardStep("s1", "X", "Y", 1)]))
        assert len(svc.incomplete_wizards("inst-2")) == 0
