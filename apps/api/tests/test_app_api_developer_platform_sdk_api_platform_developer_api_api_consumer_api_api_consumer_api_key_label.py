import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_key_label import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabel, KeyLabel,
)

class TestConsumerApiKeyLabel:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabel()
        svc.set_label("inst-1", KeyLabel(key_id="k1", consumer_id="c1", label="Main Production Key", environment="production", tags=["primary"]))
        l = svc.get_label("inst-1", "k1")
        assert l is not None and l.label == "Main Production Key"

    def test_by_environment(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabel()
        svc.set_label("inst-1", KeyLabel(key_id="k1", consumer_id="c1", label="Prod", environment="production"))
        svc.set_label("inst-1", KeyLabel(key_id="k2", consumer_id="c1", label="Test", environment="test"))
        assert len(svc.by_environment("inst-1", "production")) == 1

    def test_by_tag(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabel()
        svc.set_label("inst-1", KeyLabel(key_id="k1", consumer_id="c1", label="Key", tags=["ci", "automation"]))
        assert len(svc.by_tag("inst-1", "ci")) == 1

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabel()
        svc.set_label("inst-1", KeyLabel(key_id="k1", consumer_id="c1", label="Backend Service Key"))
        assert len(svc.search("inst-1", "backend")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabel()
        svc.set_label("inst-1", KeyLabel(key_id="k1", consumer_id="c1", label="X"))
        assert len(svc.list_labels("inst-2")) == 0
