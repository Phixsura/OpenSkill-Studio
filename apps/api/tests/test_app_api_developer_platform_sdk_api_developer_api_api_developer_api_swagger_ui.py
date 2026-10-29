import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_api_developer_api_swagger_ui import AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUI

class TestSwaggerUI:
    def test_configure(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUI()
        c = s.configure("inst-1", "My API", "2.0", "https://api.example.com", "bearer", "dark")
        assert c.auth_type == "bearer"
        assert c.theme == "dark"

    def test_https_required(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUI()
        with pytest.raises(ValueError):
            s.configure("inst-1", "API", "1.0", "http://bad.com")

    def test_invalid_auth(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUI()
        with pytest.raises(ValueError):
            s.configure("inst-1", "API", "1.0", "https://a.com", auth_type="custom")

    def test_page_views(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUI()
        s.configure("inst-1", "API", "1.0", "https://a.com")
        s.record_view("inst-1")
        s.record_view("inst-1")
        assert s.get("inst-1").page_views == 2

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUI()
        s.configure("inst-1", "API", "1.0", "https://a.com")
        assert s.get("inst-2") is None
