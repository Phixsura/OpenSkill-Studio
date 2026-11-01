import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_access_control_list import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList, ACLRule,
)

class TestEndpointAccessControlList:
    def test_explicit_allow(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList(default_policy="deny")
        svc.add_rule("inst-1", ACLRule(rule_id="r1", endpoint_path="/api/admin", consumer_id="c1", action="allow"))
        result = svc.check("inst-1", "/api/admin", "c1")
        assert result.allowed and result.reason == "explicit_allow"

    def test_explicit_deny(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList()
        svc.add_rule("inst-1", ACLRule(rule_id="r1", endpoint_path="/api/admin", consumer_id="c1", action="deny"))
        result = svc.check("inst-1", "/api/admin", "c1")
        assert not result.allowed and result.reason == "explicit_deny"

    def test_deny_takes_precedence(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList()
        svc.add_rule("inst-1", ACLRule(rule_id="r1", endpoint_path="/api", consumer_id="c1", action="allow"))
        svc.remove_rule("inst-1", "/api", "c1")
        svc.add_rule("inst-1", ACLRule(rule_id="r2", endpoint_path="/api", consumer_id="c1", action="deny"))
        result = svc.check("inst-1", "/api", "c1")
        assert not result.allowed

    def test_default_allow(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList(default_policy="allow")
        result = svc.check("inst-1", "/api", "unknown")
        assert result.allowed and result.reason == "default_allow"

    def test_default_deny(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList(default_policy="deny")
        result = svc.check("inst-1", "/api", "unknown")
        assert not result.allowed and result.reason == "default_deny"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlList()
        svc.add_rule("inst-1", ACLRule(rule_id="r1", endpoint_path="/api", consumer_id="c1", action="deny"))
        result = svc.check("inst-2", "/api", "c1")
        assert result.allowed  # default allow, no rules for inst-2
