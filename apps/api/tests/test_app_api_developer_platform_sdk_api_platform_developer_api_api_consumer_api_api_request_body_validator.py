from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_body_validator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidator, BodySchema,
)

class TestRequestBodyValidator:
    def test_valid_body(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidator()
        svc.register_schema("inst-1", BodySchema(endpoint="/users", method="POST", required_fields=["name", "email"], field_types={"name": "string", "age": "int"}))
        r = svc.validate("inst-1", "POST", "/users", '{"name":"Alice","email":"a@b.com","age":30}')
        assert r.valid is True

    def test_missing_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidator()
        svc.register_schema("inst-1", BodySchema(endpoint="/users", method="POST", required_fields=["name"]))
        r = svc.validate("inst-1", "POST", "/users", '{"email":"a@b.com"}')
        assert r.valid is False and "name" in r.errors[0]

    def test_wrong_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidator()
        svc.register_schema("inst-1", BodySchema(endpoint="/api", method="POST", field_types={"count": "int"}))
        r = svc.validate("inst-1", "POST", "/api", '{"count":"not_int"}')
        assert r.valid is False

    def test_bool_guard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidator()
        svc.register_schema("inst-1", BodySchema(endpoint="/api", method="POST", field_types={"count": "int"}))
        r = svc.validate("inst-1", "POST", "/api", '{"count":true}')
        assert r.valid is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidator()
        svc.register_schema("inst-1", BodySchema(endpoint="/api", method="POST"))
        assert len(svc.list_schemas("inst-2")) == 0
