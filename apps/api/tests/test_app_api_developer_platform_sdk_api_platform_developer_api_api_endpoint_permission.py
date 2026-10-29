from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_endpoint_permission import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermission, PermissionRule,
)

class TestEndpointPermission:
    def test_public_endpoint(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermission()
        svc.set_rule("inst-1", PermissionRule(rule_id="r1", endpoint="/health", method="GET", public=True))
        result = svc.check_access("inst-1", "GET", "/health")
        assert result["allowed"] is True

    def test_scope_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermission()
        svc.set_rule("inst-1", PermissionRule(rule_id="r1", endpoint="/admin", method="GET", required_scopes=["admin"]))
        assert svc.check_access("inst-1", "GET", "/admin", scopes=["read"])["allowed"] is False
        assert svc.check_access("inst-1", "GET", "/admin", scopes=["admin"])["allowed"] is True

    def test_role_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermission()
        svc.set_rule("inst-1", PermissionRule(rule_id="r1", endpoint="/users", method="DELETE", required_roles=["admin"]))
        assert svc.check_access("inst-1", "DELETE", "/users", roles=["viewer"])["allowed"] is False

    def test_no_rule_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermission()
        assert svc.check_access("inst-1", "GET", "/anything")["allowed"] is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermission()
        svc.set_rule("inst-1", PermissionRule(rule_id="r1", endpoint="/a", method="GET"))
        assert len(svc.list_rules("inst-2")) == 0
