from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_feature_adoption import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoption

class TestConsumerFeatureAdoption:
    def test_record_usage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoption()
        svc.register_feature("inst-1", "f1", "Webhooks")
        svc.record_usage("inst-1", "f1", "c1")
        svc.record_usage("inst-1", "f1", "c2")
        svc.record_usage("inst-1", "f1", "c1")  # duplicate
        f = svc._features[("inst-1", "f1")]
        assert f.adoption_count == 2 and f.total_usage_count == 3

    def test_adoption_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoption()
        svc.register_feature("inst-1", "f1", "Webhooks")
        svc.record_usage("inst-1", "f1", "c1")
        rates = svc.adoption_rate("inst-1", 10)
        assert rates["Webhooks"] == 10.0

    def test_consumer_features(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoption()
        svc.register_feature("inst-1", "f1", "Webhooks")
        svc.register_feature("inst-1", "f2", "SSO")
        svc.record_usage("inst-1", "f1", "c1")
        features = svc.consumer_features("inst-1", "c1")
        assert "Webhooks" in features and "SSO" not in features

    def test_least_adopted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoption()
        svc.register_feature("inst-1", "f1", "Popular")
        svc.register_feature("inst-1", "f2", "Unused")
        for i in range(10): svc.record_usage("inst-1", "f1", f"c{i}")
        least = svc.least_adopted("inst-1", 1)
        assert least[0].name == "Unused"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoption()
        svc.register_feature("inst-1", "f1", "X")
        assert len(svc.list_features("inst-2")) == 0
