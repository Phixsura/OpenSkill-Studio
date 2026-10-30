from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_response_schema import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchema, ResponseSchema,
)

class TestEndpointResponseSchema:
    def test_valid(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchema()
        svc.register("inst-1", ResponseSchema(endpoint="/users", method="GET", status_code=200, required_fields=["id", "name"], fields={"id": "string", "age": "int"}))
        errors = svc.validate("inst-1", "GET", "/users", 200, {"id": "u1", "name": "Alice", "age": 30})
        assert len(errors) == 0

    def test_missing_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchema()
        svc.register("inst-1", ResponseSchema(endpoint="/api", method="GET", status_code=200, required_fields=["id"]))
        errors = svc.validate("inst-1", "GET", "/api", 200, {"name": "test"})
        assert len(errors) == 1

    def test_wrong_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchema()
        svc.register("inst-1", ResponseSchema(endpoint="/api", method="GET", status_code=200, fields={"count": "int"}))
        errors = svc.validate("inst-1", "GET", "/api", 200, {"count": "not_int"})
        assert len(errors) == 1

    def test_no_schema_passes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchema()
        assert svc.validate("inst-1", "GET", "/unknown", 200, {}) == []

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchema()
        svc.register("inst-1", ResponseSchema(endpoint="/api", method="GET", status_code=200))
        assert len(svc.list_schemas("inst-2")) == 0
