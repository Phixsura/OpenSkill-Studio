import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_graphql_schema_registry import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistry

class TestApiGraphqlSchemaRegistry:
    def test_create_and_publish(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistry()
        svc.create_registry("inst-1", "r1", "users-api")
        sv = svc.publish_version("inst-1", "r1", "v1", "type Query { users: [User] }", type_count=2, query_count=1)
        assert sv.version == "v1"
        assert sv.type_count == 2

    def test_current_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistry()
        svc.create_registry("inst-1", "r1", "api")
        svc.publish_version("inst-1", "r1", "v1", "schema v1")
        svc.publish_version("inst-1", "r1", "v2", "schema v2")
        current = svc.get_current("inst-1", "r1")
        assert current.version == "v2"

    def test_compare(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistry()
        svc.create_registry("inst-1", "r1", "api")
        svc.publish_version("inst-1", "r1", "v1", "schema a", type_count=5, query_count=3)
        svc.publish_version("inst-1", "r1", "v2", "schema b", type_count=7, query_count=4)
        diff = svc.compare_versions("inst-1", "r1", "v1", "v2")
        assert diff["schema_changed"] is True
        assert diff["type_diff"] == 2

    def test_duplicate_registry(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistry()
        svc.create_registry("inst-1", "r1", "api")
        with pytest.raises(ValueError, match="already exists"):
            svc.create_registry("inst-1", "r1", "api")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistry()
        svc.create_registry("inst-1", "r1", "api")
        assert len(svc.list_registries("inst-2")) == 0
