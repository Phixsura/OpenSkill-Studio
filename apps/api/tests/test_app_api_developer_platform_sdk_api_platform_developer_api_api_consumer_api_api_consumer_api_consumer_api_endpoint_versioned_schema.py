import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_endpoint_versioned_schema import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema, SchemaVersion,
)

class TestEndpointVersionedSchema:
    def test_register_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema()
        svc.register("inst-1", SchemaVersion(version="v1", endpoint_path="/api/users", fields={"id": "string", "name": "string"}))
        s = svc.get("inst-1", "/api/users", "v1")
        assert s is not None and "id" in s.fields

    def test_compare_added(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema()
        svc.register("inst-1", SchemaVersion(version="v1", endpoint_path="/api", fields={"id": "string"}))
        svc.register("inst-1", SchemaVersion(version="v2", endpoint_path="/api", fields={"id": "string", "email": "string"}))
        compat = svc.compare("inst-1", "/api", "v1", "v2")
        assert "email" in compat.added_fields and not compat.breaking

    def test_compare_removed_is_breaking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema()
        svc.register("inst-1", SchemaVersion(version="v1", endpoint_path="/api", fields={"id": "string", "legacy": "string"}))
        svc.register("inst-1", SchemaVersion(version="v2", endpoint_path="/api", fields={"id": "string"}))
        compat = svc.compare("inst-1", "/api", "v1", "v2")
        assert "legacy" in compat.removed_fields and compat.breaking

    def test_type_change_is_breaking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema()
        svc.register("inst-1", SchemaVersion(version="v1", endpoint_path="/api", fields={"count": "string"}))
        svc.register("inst-1", SchemaVersion(version="v2", endpoint_path="/api", fields={"count": "integer"}))
        compat = svc.compare("inst-1", "/api", "v1", "v2")
        assert compat.type_changes["count"] == ("string", "integer") and compat.breaking

    def test_list_versions(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema()
        svc.register("inst-1", SchemaVersion(version="v2", endpoint_path="/api", fields={}))
        svc.register("inst-1", SchemaVersion(version="v1", endpoint_path="/api", fields={}))
        versions = svc.list_versions("inst-1", "/api")
        assert [v.version for v in versions] == ["v1", "v2"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema()
        svc.register("inst-1", SchemaVersion(version="v1", endpoint_path="/api", fields={}))
        assert svc.get("inst-2", "/api", "v1") is None
