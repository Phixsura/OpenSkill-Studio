import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_custom_field import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField, CustomField,
)

class TestConsumerCustomField:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField()
        svc.set_field("inst-1", "c1", CustomField(name="company", value="Acme Inc"))
        f = svc.get_field("inst-1", "c1", "company")
        assert f.value == "Acme Inc"

    def test_update(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField()
        svc.set_field("inst-1", "c1", CustomField(name="tier", value="free"))
        svc.set_field("inst-1", "c1", CustomField(name="tier", value="pro"))
        assert svc.get_field("inst-1", "c1", "tier").value == "pro"

    def test_delete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField()
        svc.set_field("inst-1", "c1", CustomField(name="temp", value="x"))
        svc.delete_field("inst-1", "c1", "temp")
        assert svc.get_field("inst-1", "c1", "temp") is None

    def test_invalid_name(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField()
        with pytest.raises(ValueError, match="Invalid field name"):
            svc.set_field("inst-1", "c1", CustomField(name="123bad", value="x"))

    def test_max_fields(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField(max_fields=2)
        svc.set_field("inst-1", "c1", CustomField(name="a", value="1"))
        svc.set_field("inst-1", "c1", CustomField(name="b", value="2"))
        with pytest.raises(ValueError, match="Max 2 fields"):
            svc.set_field("inst-1", "c1", CustomField(name="c", value="3"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomField()
        svc.set_field("inst-1", "c1", CustomField(name="x", value="1"))
        assert svc.get_field("inst-2", "c1", "x") is None
