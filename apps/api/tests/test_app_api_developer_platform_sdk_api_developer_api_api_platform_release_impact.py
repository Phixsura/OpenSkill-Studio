from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_release_impact import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpact

class TestReleaseImpact:
    def test_low_impact(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpact()
        ri = r.record("inst-1", "v2.1", error_rate_before=0.5, error_rate_after=0.5, latency_before_ms=45, latency_after_ms=46)
        assert ri.impact_severity == "low"

    def test_high_impact(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpact()
        ri = r.record("inst-1", "v3.0", error_rate_before=0.1, error_rate_after=5.0, latency_before_ms=45, latency_after_ms=200)
        assert ri.impact_severity == "high"
        assert ri.error_delta == 4.9

    def test_critical_rollback(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpact()
        ri = r.record("inst-1", "v4.0", error_rate_before=0.1, error_rate_after=20, latency_before_ms=50, latency_after_ms=2000, rollback_needed=True)
        assert ri.impact_severity == "critical"

    def test_high_impact_list(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpact()
        r.record("inst-1", "v1", error_rate_before=0.1, error_rate_after=0.1, latency_before_ms=50, latency_after_ms=50)
        r.record("inst-1", "v2", error_rate_before=0.1, error_rate_after=5, latency_before_ms=50, latency_after_ms=200)
        assert len(r.high_impact_releases("inst-1")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpact()
        r.record("inst-1", "v1", error_rate_before=0, error_rate_after=0, latency_before_ms=0, latency_after_ms=0)
        assert len(r.all_impacts("inst-2")) == 0
