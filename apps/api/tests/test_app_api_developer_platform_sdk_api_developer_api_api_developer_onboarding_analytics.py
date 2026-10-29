from app.services.app_api_developer_platform_sdk_api_developer_api_api_developer_onboarding_analytics import AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalytics

class TestOnboardingAnalytics:
    def test_excellent(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalytics()
        o = a.update("inst-1", total_started=100, total_completed=85)
        assert o.completion_rate == 85.0
        assert o.quality == "excellent"

    def test_poor(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalytics()
        o = a.update("inst-1", total_started=100, total_completed=20)
        assert o.quality == "poor"

    def test_default(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalytics()
        assert a.get("inst-1").completion_rate == 0.0

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalytics()
        a.update("inst-1", total_started=100, total_completed=80)
        assert a.get("inst-2").total_started == 0
