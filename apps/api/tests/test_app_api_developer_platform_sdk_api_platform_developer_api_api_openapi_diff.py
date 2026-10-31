import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_openapi_diff import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiff

class TestOpenapiDiff:
    def test_endpoint_added(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiff()
        svc.register_spec("inst-1", "v1", {"/users": ["id", "name"]})
        svc.register_spec("inst-1", "v2", {"/users": ["id", "name"], "/orders": ["id"]})
        diff = svc.diff("inst-1", "v1", "v2")
        added = [c for c in diff.changes if c.change_type == "endpoint_added"]
        assert len(added) == 1

    def test_endpoint_removed_is_breaking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiff()
        svc.register_spec("inst-1", "v1", {"/users": ["id"], "/legacy": ["x"]})
        svc.register_spec("inst-1", "v2", {"/users": ["id"]})
        diff = svc.diff("inst-1", "v1", "v2")
        assert diff.breaking_count == 1

    def test_field_changes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiff()
        svc.register_spec("inst-1", "v1", {"/users": ["id", "name", "email"]})
        svc.register_spec("inst-1", "v2", {"/users": ["id", "name", "phone"]})
        diff = svc.diff("inst-1", "v1", "v2")
        assert diff.breaking_count == 1  # email removed
        assert diff.non_breaking_count == 1  # phone added

    def test_no_changes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiff()
        svc.register_spec("inst-1", "v1", {"/users": ["id"]})
        svc.register_spec("inst-1", "v2", {"/users": ["id"]})
        diff = svc.diff("inst-1", "v1", "v2")
        assert len(diff.changes) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiff()
        svc.register_spec("inst-1", "v1", {"/a": []})
        assert svc.versions("inst-2") == []
