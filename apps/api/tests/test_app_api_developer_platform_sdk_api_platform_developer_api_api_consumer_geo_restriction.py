import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_geo_restriction import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestriction, GeoPolicy,
)

class TestConsumerGeoRestriction:
    def test_allowlist(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="allowlist", regions=["US", "CA", "GB"]))
        assert svc.check_access("inst-1", "c1", "US")["allowed"] is True
        assert svc.check_access("inst-1", "c1", "CN")["allowed"] is False

    def test_blocklist(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="blocklist", regions=["RU", "KP"]))
        assert svc.check_access("inst-1", "c1", "US")["allowed"] is True
        assert svc.check_access("inst-1", "c1", "RU")["allowed"] is False

    def test_no_policy_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestriction()
        assert svc.check_access("inst-1", "c1", "US")["allowed"] is True

    def test_invalid_country_code(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestriction()
        with pytest.raises(ValueError, match="Invalid country"):
            svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="allowlist", regions=["123"]))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="allowlist", regions=["US"]))
        assert svc.consumer_count("inst-2") == 0
