import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_platform_feature_adoption import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoption

class TestFeatureAdoption:
    def test_track(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoption()
        f = a.track("inst-1", "webhooks", 100, 80)
        assert f.adoption_pct == 80.0
        assert f.adoption_tier == "mainstream"

    def test_early_adopters(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoption()
        f = a.track("inst-1", "graphql", 100, 20)
        assert f.adoption_tier == "early_adopters"

    def test_low_adoption(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoption()
        a.track("inst-1", "popular", 100, 90)
        a.track("inst-1", "niche", 100, 5)
        assert len(a.low_adoption("inst-1", 20)) == 1

    def test_adopters_exceed_guard(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoption()
        with pytest.raises(ValueError):
            a.track("inst-1", "x", 10, 20)

    def test_isolation(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoption()
        a.track("inst-1", "webhooks", 100, 50)
        assert len(a.all_features("inst-2")) == 0
