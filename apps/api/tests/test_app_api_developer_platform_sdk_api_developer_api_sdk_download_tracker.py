from app.services.app_api_developer_platform_sdk_api_developer_api_sdk_download_tracker import AppAPIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTracker

class TestSDKDownloadTracker:
    def test_record(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTracker()
        d = t.record("inst-1", "openskill-sdk", "1.0.0", "python", 100)
        assert d.downloads == 100

    def test_accumulate(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTracker()
        t.record("inst-1", "sdk", "1.0", "python", 50)
        t.record("inst-1", "sdk", "1.0", "python", 30)
        assert t.total_downloads("inst-1") == 80

    def test_by_language(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTracker()
        t.record("inst-1", "sdk", "1.0", "python", 100)
        t.record("inst-1", "sdk", "1.0", "javascript", 200)
        assert t.by_language("inst-1") == {"python": 100, "javascript": 200}

    def test_popular(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTracker()
        t.record("inst-1", "sdk-a", "1.0", "python", 500)
        t.record("inst-1", "sdk-b", "1.0", "python", 100)
        pop = t.popular_sdks("inst-1", 1)
        assert pop[0][0] == "sdk-a"

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTracker()
        t.record("inst-1", "sdk", "1.0", "python", 100)
        assert t.total_downloads("inst-2") == 0
