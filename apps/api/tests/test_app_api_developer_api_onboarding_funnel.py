from app.services.app_api_developer_api_onboarding_funnel import AppAPIDeveloperAPIOnboardingFunnel

class TestFunnel:
    def test_set(self):
        f = AppAPIDeveloperAPIOnboardingFunnel()
        funnel = f.set_funnel("inst-1", [
            {"name": "Sign Up", "entered": 1000, "completed": 800},
            {"name": "Create App", "entered": 800, "completed": 500},
            {"name": "First API Call", "entered": 500, "completed": 300},
        ])
        assert funnel.overall_conversion == 30.0
        assert funnel.stages[0].conversion_rate == 80.0

    def test_default(self):
        f = AppAPIDeveloperAPIOnboardingFunnel()
        assert f.get("inst-1") is None

    def test_isolation(self):
        f = AppAPIDeveloperAPIOnboardingFunnel()
        f.set_funnel("inst-1", [{"name": "S1", "entered": 100, "completed": 50}])
        assert f.get("inst-2") is None
