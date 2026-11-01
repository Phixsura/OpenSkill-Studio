import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_environment_variable import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable, EnvVariable,
)

class TestConsumerApiEnvironmentVariable:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable()
        svc.set_variable("inst-1", "c1", EnvVariable(key="API_KEY", value="abc123", environment="production"), now=self._now())
        v = svc.get_variable("inst-1", "c1", "production", "API_KEY")
        assert v.value == "abc123"

    def test_sensitive_masked(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable()
        svc.set_variable("inst-1", "c1", EnvVariable(key="SECRET", value="s3cret", sensitive=True), now=self._now())
        v = svc.get_variable("inst-1", "c1", "production", "SECRET")
        assert v.value == "***"

    def test_delete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable()
        svc.set_variable("inst-1", "c1", EnvVariable(key="TEMP", value="x"), now=self._now())
        svc.delete_variable("inst-1", "c1", "production", "TEMP")
        assert svc.get_variable("inst-1", "c1", "production", "TEMP") is None

    def test_copy_environment(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable()
        svc.set_variable("inst-1", "c1", EnvVariable(key="DB_URL", value="prod-db", environment="production"), now=self._now())
        copied = svc.copy_to_environment("inst-1", "c1", "production", "staging", now=self._now())
        assert copied == 1
        v = svc.get_variable("inst-1", "c1", "staging", "DB_URL")
        assert v.value == "prod-db"

    def test_list_sorted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable()
        svc.set_variable("inst-1", "c1", EnvVariable(key="Z_VAR", value="z"), now=self._now())
        svc.set_variable("inst-1", "c1", EnvVariable(key="A_VAR", value="a"), now=self._now())
        vars = svc.list_variables("inst-1", "c1", "production")
        assert vars[0].key == "A_VAR"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEnvironmentVariable()
        svc.set_variable("inst-1", "c1", EnvVariable(key="X", value="y"), now=self._now())
        assert svc.get_variable("inst-2", "c1", "production", "X") is None
