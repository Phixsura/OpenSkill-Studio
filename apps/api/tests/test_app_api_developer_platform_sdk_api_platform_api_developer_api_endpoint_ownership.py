from app.services.app_api_developer_platform_sdk_api_platform_api_developer_api_endpoint_ownership import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnership

class TestEndpointOwnership:
    def test_assign(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnership()
        eo = o.assign("inst-1", "/api/users", "platform-team", "oncall@acme.com", "critical")
        assert eo.owner_team == "platform-team"

    def test_by_team(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnership()
        o.assign("inst-1", "/api/users", "platform")
        o.assign("inst-1", "/api/orders", "commerce")
        o.assign("inst-1", "/api/billing", "platform")
        assert len(o.by_team("inst-1", "platform")) == 2

    def test_unowned(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnership()
        o.assign("inst-1", "/api/users", "platform")
        unowned = o.unowned("inst-1", ["/api/users", "/api/orders", "/api/billing"])
        assert unowned == ["/api/orders", "/api/billing"]

    def test_team_distribution(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnership()
        o.assign("inst-1", "/a", "team-a")
        o.assign("inst-1", "/b", "team-a")
        o.assign("inst-1", "/c", "team-b")
        assert o.team_distribution("inst-1") == {"team-a": 2, "team-b": 1}

    def test_isolation(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnership()
        o.assign("inst-1", "/api", "team")
        assert len(o.all_ownership("inst-2")) == 0
