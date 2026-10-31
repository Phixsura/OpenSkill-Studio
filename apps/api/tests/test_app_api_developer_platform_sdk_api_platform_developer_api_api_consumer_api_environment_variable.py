import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_environment_variable import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariable, EnvVar,
)

class TestEnvironmentVariable:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariable()
        svc.set_var("inst-1", "c1", EnvVar(key="API_URL", value="https://api.example.com"))
        var = svc.get_var("inst-1", "c1", "API_URL")
        assert var is not None and var.value == "https://api.example.com"

    def test_secret_masked(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariable()
        svc.set_var("inst-1", "c1", EnvVar(key="DB_PASSWORD", value="super-secret-password", secret=True))
        var = svc.get_var("inst-1", "c1", "DB_PASSWORD")
        assert var.value.startswith("***")
        assert "super-secret" not in var.value

    def test_invalid_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariable()
        with pytest.raises(ValueError, match="Invalid key"):
            svc.set_var("inst-1", "c1", EnvVar(key="bad-key", value="x"))

    def test_delete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariable()
        svc.set_var("inst-1", "c1", EnvVar(key="MY_VAR", value="test"))
        assert svc.delete_var("inst-1", "c1", "MY_VAR") is True
        assert svc.get_var("inst-1", "c1", "MY_VAR") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEnvironmentVariable()
        svc.set_var("inst-1", "c1", EnvVar(key="MY_VAR", value="x"))
        assert svc.var_count("inst-2", "c1") == 0
