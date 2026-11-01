import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_data_residency import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidency, ResidencyConfig,
)

class TestDataResidency:
    def test_configure_and_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidency()
        svc.configure("inst-1", ResidencyConfig(consumer_id="c1", primary_region="eu-west", allowed_regions=["eu-west", "eu-central"], compliance_frameworks=["gdpr"]))
        assert svc.check_region("inst-1", "c1", "eu-west") is True
        assert svc.check_region("inst-1", "c1", "us-east") is False

    def test_primary_auto_added(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidency()
        config = svc.configure("inst-1", ResidencyConfig(consumer_id="c1", primary_region="ap-south", allowed_regions=[]))
        assert "ap-south" in config.allowed_regions

    def test_invalid_region(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidency()
        with pytest.raises(ValueError, match="Invalid region"):
            svc.configure("inst-1", ResidencyConfig(consumer_id="c1", primary_region="mars-1"))

    def test_consumers_in_region(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidency()
        svc.configure("inst-1", ResidencyConfig(consumer_id="c1", primary_region="eu-west"))
        svc.configure("inst-1", ResidencyConfig(consumer_id="c2", primary_region="us-east"))
        assert svc.consumers_in_region("inst-1", "eu-west") == ["c1"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidency()
        svc.configure("inst-1", ResidencyConfig(consumer_id="c1", primary_region="us-east"))
        assert len(svc.list_configs("inst-2")) == 0
