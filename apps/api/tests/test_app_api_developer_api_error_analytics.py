from app.services.app_api_developer_api_error_analytics import AppAPIDeveloperAPIErrorAnalytics

class TestErrorAnalytics:
    def test_update(self):
        a = AppAPIDeveloperAPIErrorAnalytics()
        ea = a.update("inst-1", total_errors=500, unique_error_codes=15, top_error_code="AUTH_FAIL", top_error_count=200)
        assert ea.top_error_code == "AUTH_FAIL"

    def test_default(self):
        a = AppAPIDeveloperAPIErrorAnalytics()
        assert a.get("inst-1").total_errors == 0

    def test_isolation(self):
        a = AppAPIDeveloperAPIErrorAnalytics()
        a.update("inst-1", total_errors=100)
        assert a.get("inst-2").total_errors == 0
