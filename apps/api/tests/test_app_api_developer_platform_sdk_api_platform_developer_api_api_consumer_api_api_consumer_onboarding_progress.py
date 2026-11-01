from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_onboarding_progress import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgress, OnboardingPhase,
)

def make_phases():
    return [OnboardingPhase("p1", "Register", 1), OnboardingPhase("p2", "Configure", 2), OnboardingPhase("p3", "Test", 3, required=False)]

class TestConsumerOnboardingProgress:
    def test_create_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgress()
        p = svc.create("inst-1", "c1", make_phases())
        assert p.completion_pct == 0.0
        assert p.current_phase == "Register"

    def test_complete_to_ready(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgress()
        svc.create("inst-1", "c1", make_phases())
        svc.complete_phase("inst-1", "c1", "p1")
        svc.complete_phase("inst-1", "c1", "p2")
        p = svc.get_progress("inst-1", "c1")
        assert p.ready is True  # p3 is optional

    def test_not_ready_without_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgress()
        svc.create("inst-1", "c1", make_phases())
        svc.complete_phase("inst-1", "c1", "p3")
        assert svc.get_progress("inst-1", "c1").ready is False

    def test_incomplete_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgress()
        svc.create("inst-1", "c1", make_phases())
        assert len(svc.incomplete("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgress()
        svc.create("inst-1", "c1", [OnboardingPhase("p1", "X", 1)])
        assert len(svc.list_progress("inst-2")) == 0
