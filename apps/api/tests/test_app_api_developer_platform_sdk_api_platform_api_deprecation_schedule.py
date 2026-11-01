from app.services.app_api_developer_platform_sdk_api_platform_api_deprecation_schedule import AppAPIDeveloperPlatformSDKApiPlatformApiDeprecationSchedule

class TestDeprecationSchedule:
    def test_schedule(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiDeprecationSchedule()
        d = s.schedule("inst-1", "/api/v1/users", "v1", "2025-01-01", "2025-06-01", "/api/v2/users")
        assert d.replacement == "/api/v2/users"

    def test_urgency(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiDeprecationSchedule()
        s.schedule("inst-1", "/old", "v1", "2025-01", "2025-06")
        s.update_migration("inst-1", "/old", "v1", 50, 30)
        assert s.all_schedules("inst-1")[0].urgency == "critical"

    def test_done(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiDeprecationSchedule()
        s.schedule("inst-1", "/old", "v1", "2025-01", "2025-06")
        s.update_migration("inst-1", "/old", "v1", 0, 100)
        assert s.all_schedules("inst-1")[0].urgency == "done"

    def test_critical_list(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiDeprecationSchedule()
        s.schedule("inst-1", "/a", "v1", "2025-01", "2025-06")
        s.schedule("inst-1", "/b", "v1", "2025-01", "2025-06")
        s.update_migration("inst-1", "/a", "v1", 50, 30)
        s.update_migration("inst-1", "/b", "v1", 0, 100)
        assert len(s.critical_deprecations("inst-1")) == 1

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiDeprecationSchedule()
        s.schedule("inst-1", "/old", "v1", "2025-01", "2025-06")
        assert len(s.all_schedules("inst-2")) == 0
