from app.services.app_api_developer_api_platform_sdk_session_grand_total import AppAPIDeveloperPlatformSDKSessionGrandTotal

class TestSessionGrandTotal:
    def test_record(self):
        t = AppAPIDeveloperPlatformSDKSessionGrandTotal()
        s = t.record("inst-1", session_commits=164, session_pairs=544, all_time_commits=764, all_time_backend=544, all_time_frontend=544)
        assert s.total_components == 1088

    def test_default(self):
        t = AppAPIDeveloperPlatformSDKSessionGrandTotal()
        s = t.get("inst-1")
        assert s.session_commits == 0

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKSessionGrandTotal()
        t.record("inst-1", session_commits=100)
        assert t.get("inst-2").session_commits == 0
