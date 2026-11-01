from app.services.app_api_developer_platform_sdk_api_consumer_api_version_adoption import AppAPIDeveloperPlatformSDKApiConsumerApiVersionAdoption

class TestConsumerVersionAdoption:
    def test_record(self):
        a = AppAPIDeveloperPlatformSDKApiConsumerApiVersionAdoption()
        v = a.record("inst-1", "c1", "v2.0", 100)
        assert v.primary_version == "v2.0"
        assert v.using_latest is True

    def test_multi_version(self):
        a = AppAPIDeveloperPlatformSDKApiConsumerApiVersionAdoption()
        a.record("inst-1", "c1", "v1.0", 50)
        a.record("inst-1", "c1", "v2.0", 100)
        v = a.all_adoptions("inst-1")[0]
        assert v.multi_version is True
        assert v.primary_version == "v2.0"

    def test_on_old_versions(self):
        a = AppAPIDeveloperPlatformSDKApiConsumerApiVersionAdoption()
        a.record("inst-1", "c1", "v1.0", 100)
        a.record("inst-1", "c2", "v2.0", 100)
        assert len(a.on_old_versions("inst-1")) == 1

    def test_distribution(self):
        a = AppAPIDeveloperPlatformSDKApiConsumerApiVersionAdoption()
        a.record("inst-1", "c1", "v1.0", 100)
        a.record("inst-1", "c2", "v2.0", 200)
        dist = a.version_distribution("inst-1")
        assert dist == {"v1.0": 100, "v2.0": 200}

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKApiConsumerApiVersionAdoption()
        a.record("inst-1", "c1", "v1.0")
        assert len(a.all_adoptions("inst-2")) == 0
