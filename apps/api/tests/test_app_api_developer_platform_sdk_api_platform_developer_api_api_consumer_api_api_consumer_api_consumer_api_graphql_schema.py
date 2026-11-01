import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_graphql_schema import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchema, GraphQLType, GraphQLField, FieldAccessRule,
)

class TestConsumerApiGraphqlSchema:
    def test_register_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchema()
        svc.register_type("inst-1", GraphQLType(type_name="User", fields=[GraphQLField(name="id", field_type="ID"), GraphQLField(name="email", field_type="String")]))
        t = svc.get_type("inst-1", "User")
        assert t is not None and len(t.fields) == 2

    def test_field_access_restriction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchema()
        svc.register_type("inst-1", GraphQLType(type_name="User", fields=[GraphQLField(name="id", field_type="ID"), GraphQLField(name="email", field_type="String"), GraphQLField(name="ssn", field_type="String")]))
        svc.set_field_access("inst-1", FieldAccessRule(type_name="User", field_name="ssn", consumer_id="c1", allowed=False))
        visible = svc.get_visible_fields("inst-1", "c1", "User")
        names = [f.name for f in visible]
        assert "id" in names and "email" in names and "ssn" not in names

    def test_all_visible_without_rules(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchema()
        svc.register_type("inst-1", GraphQLType(type_name="Post", fields=[GraphQLField(name="title", field_type="String")]))
        visible = svc.get_visible_fields("inst-1", "c1", "Post")
        assert len(visible) == 1

    def test_introspect(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchema()
        svc.register_type("inst-1", GraphQLType(type_name="User"))
        svc.register_type("inst-1", GraphQLType(type_name="Post"))
        types = svc.introspect("inst-1")
        assert len(types) == 2 and types[0].type_name == "Post"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchema()
        svc.register_type("inst-1", GraphQLType(type_name="User"))
        assert svc.get_type("inst-2", "User") is None
