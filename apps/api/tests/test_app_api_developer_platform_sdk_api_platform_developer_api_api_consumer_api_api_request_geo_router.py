from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_geo_router import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouter, GeoRoutingConfig, RegionalBackend,
)

class TestRequestGeoRouter:
    def test_route_to_preferred(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouter()
        svc.configure("inst-1", GeoRoutingConfig(backends=[RegionalBackend("us-east", "https://us.api.com"), RegionalBackend("eu-west", "https://eu.api.com")]))
        svc.set_consumer_region("inst-1", "c1", "eu-west")
        b = svc.route("inst-1", "c1")
        assert b.region == "eu-west"

    def test_fallback_on_unhealthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouter()
        svc.configure("inst-1", GeoRoutingConfig(default_region="us-east", fallback_region="eu-west", backends=[
            RegionalBackend("us-east", "https://us.api.com", healthy=False),
            RegionalBackend("eu-west", "https://eu.api.com", healthy=True),
        ]))
        b = svc.route("inst-1", "c1")
        assert b.region == "eu-west"

    def test_lowest_load(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouter()
        svc.configure("inst-1", GeoRoutingConfig(default_region="ap-south", fallback_region="ap-south", backends=[
            RegionalBackend("us-east", "https://us.api.com", load_pct=80),
            RegionalBackend("eu-west", "https://eu.api.com", load_pct=20),
        ]))
        b = svc.route("inst-1", "c1")
        assert b.region == "eu-west"

    def test_no_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouter()
        assert svc.route("inst-1", "c1") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestGeoRouter()
        svc.configure("inst-1", GeoRoutingConfig(backends=[RegionalBackend("us", "https://x.com")]))
        assert len(svc.healthy_regions("inst-2")) == 0
