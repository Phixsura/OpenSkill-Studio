from app.services.app_api_developer_platform_sdk_api_platform_developer_api_output_transformer import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformer

class TestOutputTransformer:
    def test_remove(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformer()
        t.add_rule("inst-1", "/api", "r1", "remove", "internal_id")
        result = t.transform("inst-1", "/api", {"id": "1", "internal_id": "secret"})
        assert "internal_id" not in result
        assert result["id"] == "1"

    def test_rename(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformer()
        t.add_rule("inst-1", "/api", "r1", "rename", "name", {"to": "full_name"})
        result = t.transform("inst-1", "/api", {"name": "Alice"})
        assert result["full_name"] == "Alice"
        assert "name" not in result

    def test_add(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformer()
        t.add_rule("inst-1", "/api", "r1", "add", "version", {"value": "2.0"})
        result = t.transform("inst-1", "/api", {"data": "test"})
        assert result["version"] == "2.0"

    def test_mask(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformer()
        t.add_rule("inst-1", "/api", "r1", "mask", "ssn")
        result = t.transform("inst-1", "/api", {"ssn": "123-45-6789"})
        assert result["ssn"].endswith("6789")
        assert result["ssn"].startswith("***")

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiOutputTransformer()
        t.add_rule("inst-1", "/api", "r1", "remove", "x")
        assert len(t.rules_for("inst-2", "/api")) == 0
