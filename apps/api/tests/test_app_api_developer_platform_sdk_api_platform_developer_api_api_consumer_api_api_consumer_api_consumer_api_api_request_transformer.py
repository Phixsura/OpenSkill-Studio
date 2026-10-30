import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_request_transformer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer, RequestTransformRule,
)

class TestConsumerApiRequestTransformer:
    def test_add_header(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer()
        svc.add_rule("inst-1", "c1", RequestTransformRule(rule_id="r1", target="header", action="add", field_name="X-Custom", value="hello"))
        result = svc.transform("inst-1", "c1", {}, {}, {})
        assert result.headers["X-Custom"] == "hello" and result.rules_applied == 1

    def test_remove_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer()
        svc.add_rule("inst-1", "c1", RequestTransformRule(rule_id="r1", target="query", action="remove", field_name="debug"))
        result = svc.transform("inst-1", "c1", {}, {"debug": "true", "page": "1"}, {})
        assert "debug" not in result.query_params and "page" in result.query_params

    def test_rename_body_field(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer()
        svc.add_rule("inst-1", "c1", RequestTransformRule(rule_id="r1", target="body", action="rename", field_name="user_name", new_name="username"))
        result = svc.transform("inst-1", "c1", {}, {}, {"user_name": "alice"})
        assert result.body["username"] == "alice" and "user_name" not in result.body

    def test_set_overwrites(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer()
        svc.add_rule("inst-1", "c1", RequestTransformRule(rule_id="r1", target="header", action="set", field_name="Accept", value="application/json"))
        result = svc.transform("inst-1", "c1", {"Accept": "text/html"}, {}, {})
        assert result.headers["Accept"] == "application/json"

    def test_no_rules(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer()
        result = svc.transform("inst-1", "c1", {"A": "1"}, {"b": "2"}, {"c": 3})
        assert result.rules_applied == 0 and result.headers == {"A": "1"}

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer()
        svc.add_rule("inst-1", "c1", RequestTransformRule(rule_id="r1", target="header", action="add", field_name="X", value="y"))
        result = svc.transform("inst-2", "c1", {}, {}, {})
        assert result.rules_applied == 0
