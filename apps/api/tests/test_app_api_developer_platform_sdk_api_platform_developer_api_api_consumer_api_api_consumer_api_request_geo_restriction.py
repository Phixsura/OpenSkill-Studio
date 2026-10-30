import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_geo_restriction import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction, GeoPolicy,
)

class TestRequestGeoRestriction:
    def test_allowlist_allowed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="allowlist", countries={"US", "CA"}))
        result = svc.check("inst-1", "c1", "US")
        assert result.allowed and result.reason == "allowed_country"

    def test_allowlist_blocked(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="allowlist", countries={"US"}))
        result = svc.check("inst-1", "c1", "CN")
        assert not result.allowed

    def test_blocklist(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="blocklist", countries={"RU"}))
        assert svc.check("inst-1", "c1", "US").allowed
        assert not svc.check("inst-1", "c1", "RU").allowed

    def test_no_policy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction()
        result = svc.check("inst-1", "c1", "JP")
        assert result.allowed and result.reason == "no_policy"

    def test_case_insensitive(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="allowlist", countries={"us"}))
        assert svc.check("inst-1", "c1", "US").allowed

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestriction()
        svc.set_policy("inst-1", "c1", GeoPolicy(policy_id="p1", mode="blocklist", countries={"US"}))
        assert svc.check("inst-2", "c1", "US").allowed  # no policy for inst-2
