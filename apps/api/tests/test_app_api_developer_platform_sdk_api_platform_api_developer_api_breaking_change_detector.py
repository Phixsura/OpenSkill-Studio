from app.services.app_api_developer_platform_sdk_api_platform_api_developer_api_breaking_change_detector import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetector

class TestBreakingChangeDetector:
    def test_detect(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetector()
        c = d.detect("inst-1", "c1", "/api/users", "field_removed", "Removed email field", 50)
        assert c.severity == "high"

    def test_critical_endpoint_removal(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetector()
        c = d.detect("inst-1", "c1", "/api/old", "endpoint_removed", "Removed endpoint")
        assert c.severity == "critical"

    def test_critical_list(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetector()
        d.detect("inst-1", "c1", "/api/old", "endpoint_removed", "Removed")
        d.detect("inst-1", "c2", "/api/users", "field_removed", "Field removed", 5)
        assert len(d.critical_changes("inst-1")) == 1

    def test_total_affected(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetector()
        d.detect("inst-1", "c1", "/a", "field_removed", "x", 50)
        d.detect("inst-1", "c2", "/b", "type_changed", "y", 30)
        assert d.total_affected("inst-1") == 80

    def test_isolation(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetector()
        d.detect("inst-1", "c1", "/api", "field_removed", "x")
        assert len(d.all_changes("inst-2")) == 0
