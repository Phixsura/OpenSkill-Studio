import pytest
from app.services.app_api_developer_api_api_consumer_onboarding_funnel import AppAPIDeveloperAPIApiConsumerOnboardingFunnel

class TestOnboardingFunnel:
    def test_enter_and_complete(self):
        f = AppAPIDeveloperAPIApiConsumerOnboardingFunnel()
        f.enter_step("inst-1", "c1", "signup")
        m = f.complete_step("inst-1", "c1", "signup")
        assert m.entered == 1
        assert m.completed == 1

    def test_no_double_enter(self):
        f = AppAPIDeveloperAPIApiConsumerOnboardingFunnel()
        f.enter_step("inst-1", "c1", "signup")
        f.enter_step("inst-1", "c1", "signup")
        m = f.funnel("inst-1")[0]
        assert m.entered == 1

    def test_funnel_view(self):
        f = AppAPIDeveloperAPIApiConsumerOnboardingFunnel()
        for c in ["c1", "c2", "c3"]:
            f.complete_step("inst-1", c, "signup")
        for c in ["c1", "c2"]:
            f.complete_step("inst-1", c, "api_key_created")
        funnel = f.funnel("inst-1")
        assert funnel[0].completed == 3
        assert funnel[1].completed == 2

    def test_overall_conversion(self):
        f = AppAPIDeveloperAPIApiConsumerOnboardingFunnel()
        for c in ["c1", "c2", "c3", "c4"]:
            f.enter_step("inst-1", c, "signup")
        f.complete_step("inst-1", "c1", "production_traffic")
        assert f.overall_conversion("inst-1") == 25.0

    def test_isolation(self):
        f = AppAPIDeveloperAPIApiConsumerOnboardingFunnel()
        f.complete_step("inst-1", "c1", "signup")
        assert f.overall_conversion("inst-2") == 0.0
