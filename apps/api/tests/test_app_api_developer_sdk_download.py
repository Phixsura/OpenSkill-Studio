from app.services.app_api_developer_sdk_download import AppAPIDeveloperSDKDownload

class TestDownload:
    def test_record(self):
        d = AppAPIDeveloperSDKDownload()
        sd = d.record("inst-1", "python", "2.0.0")
        assert sd.download_count == 1

    def test_accumulate(self):
        d = AppAPIDeveloperSDKDownload()
        d.record("inst-1", "python", "2.0.0")
        d.record("inst-1", "python", "2.0.0")
        assert d.total_downloads("inst-1") == 2

    def test_top_languages(self):
        d = AppAPIDeveloperSDKDownload()
        for _ in range(10): d.record("inst-1", "javascript", "1.0")
        for _ in range(5): d.record("inst-1", "python", "1.0")
        top = d.top_languages("inst-1")
        assert top[0]["language"] == "javascript"

    def test_isolation(self):
        d = AppAPIDeveloperSDKDownload()
        d.record("inst-1", "python", "1.0")
        assert d.total_downloads("inst-2") == 0
