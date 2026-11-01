from app.services.app_api_developer_platform_sdk_api_platform_release_readiness import AppAPIDeveloperPlatformSDKApiPlatformReleaseReadiness

class TestReleaseReadiness:
    def test_ship_it(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformReleaseReadiness()
        rr = r.create("inst-1", "v2.0", [
            {"name": "Tests pass", "passed": True},
            {"name": "Security scan", "passed": True},
            {"name": "Docs updated", "passed": True},
        ])
        assert rr.verdict == "SHIP_IT"

    def test_hold(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformReleaseReadiness()
        rr = r.create("inst-1", "v2.0", [
            {"name": "Tests pass", "passed": True},
            {"name": "Security scan", "passed": False, "required": True},
        ])
        assert rr.verdict == "HOLD"

    def test_ship_with_caveats(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformReleaseReadiness()
        rr = r.create("inst-1", "v2.0", [
            {"name": "Tests", "passed": True, "required": True},
            {"name": "Perf test", "passed": False, "required": False},
        ])
        assert rr.verdict == "SHIP_WITH_CAVEATS"

    def test_readiness_pct(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformReleaseReadiness()
        rr = r.create("inst-1", "v2.0", [
            {"name": "A", "passed": True},
            {"name": "B", "passed": False},
        ])
        assert rr.readiness_pct == 50.0

    def test_isolation(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformReleaseReadiness()
        r.create("inst-1", "v1.0", [{"name": "A", "passed": True}])
        assert len(r.all_releases("inst-2")) == 0
