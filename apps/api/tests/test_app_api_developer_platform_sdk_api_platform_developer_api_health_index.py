from app.services.app_api_developer_platform_sdk_api_platform_developer_api_health_index import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndex

class TestHealthIndex:
    def test_perfect(self):
        h = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndex()
        idx = h.update("inst-1")
        assert idx.index == 100.0
        assert idx.grade == "A+"
        assert idx.trend_emoji == "🟢"

    def test_weighted(self):
        h = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndex()
        idx = h.update("inst-1", availability_score=90, latency_score=80, error_rate_score=85, webhook_score=95, security_score=90, dx_score=75)
        assert 80 < idx.index < 95
        assert idx.grade in ("A", "B+", "B")

    def test_poor(self):
        h = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndex()
        idx = h.update("inst-1", availability_score=50, error_rate_score=40)
        assert idx.grade in ("D", "F")
        assert idx.trend_emoji == "🔴"

    def test_isolation(self):
        h = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndex()
        h.update("inst-1", availability_score=50)
        assert h.get("inst-2").index == 100.0
