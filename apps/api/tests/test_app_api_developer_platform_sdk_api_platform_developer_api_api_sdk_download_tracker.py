from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_sdk_download_tracker import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTracker

class TestApiSdkDownloadTracker:
    def test_record_and_total(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTracker()
        svc.record_download("inst-1", "my-sdk", "1.0.0", "python", 100)
        svc.record_download("inst-1", "my-sdk", "1.1.0", "python", 200)
        assert svc.total_downloads("inst-1") == 300

    def test_by_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTracker()
        svc.record_download("inst-1", "sdk", "1.0", "typescript", 50)
        svc.record_download("inst-1", "sdk", "2.0", "typescript", 150)
        versions = svc.by_version("inst-1", "sdk")
        assert versions["1.0"] == 50 and versions["2.0"] == 150

    def test_by_language(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTracker()
        svc.record_download("inst-1", "sdk", "1.0", "python", 100)
        svc.record_download("inst-1", "sdk-ts", "1.0", "typescript", 200)
        langs = svc.by_language("inst-1")
        assert langs["python"] == 100 and langs["typescript"] == 200

    def test_accumulate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTracker()
        svc.record_download("inst-1", "sdk", "1.0", "go", 10)
        svc.record_download("inst-1", "sdk", "1.0", "go", 20)
        assert svc.total_downloads("inst-1") == 30

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTracker()
        svc.record_download("inst-1", "sdk", "1.0", "python", 100)
        assert svc.sdk_count("inst-2") == 0
