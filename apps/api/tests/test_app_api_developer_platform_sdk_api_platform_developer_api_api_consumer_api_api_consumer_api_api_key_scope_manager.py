import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_api_key_scope_manager import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager, KeyScope,
)

class TestApiKeyScopeManager:
    def test_grant_and_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager()
        svc.grant("inst-1", "k1", "read:users")
        result = svc.check("inst-1", "k1", "read:users")
        assert result.allowed and result.reason == "granted"

    def test_deny_overrides_grant(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager()
        svc.grant("inst-1", "k1", "write:orders")
        svc.deny("inst-1", "k1", "write:orders")
        result = svc.check("inst-1", "k1", "write:orders")
        assert not result.allowed and result.reason == "explicitly_denied"

    def test_wildcard_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager()
        svc.grant("inst-1", "k1", "read:*")
        result = svc.check("inst-1", "k1", "read:users")
        assert result.allowed and result.reason == "wildcard_match"

    def test_not_granted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager()
        svc.set_scopes("inst-1", KeyScope(key_id="k1", scopes={"read:users"}))
        result = svc.check("inst-1", "k1", "write:orders")
        assert not result.allowed and result.reason == "not_granted"

    def test_key_not_found(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager()
        result = svc.check("inst-1", "missing", "read:users")
        assert not result.allowed and result.reason == "key_not_found"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManager()
        svc.grant("inst-1", "k1", "read:users")
        assert svc.check("inst-2", "k1", "read:users").reason == "key_not_found"
