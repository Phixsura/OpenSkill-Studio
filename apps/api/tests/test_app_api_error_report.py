from app.services.app_api_error_report import AppAPIErrorReport

class TestReport:
    def test_generate(self):
        r = AppAPIErrorReport()
        report = r.generate("inst-1", "r1", "2024-01", [{"code": "AUTH_FAIL", "count": 50}, {"code": "NOT_FOUND", "count": 30}], 10000)
        assert report.total_errors == 80
        assert report.error_rate == 0.8

    def test_get(self):
        r = AppAPIErrorReport()
        r.generate("inst-1", "r1", "2024-01", [], 1000)
        assert r.get_report("inst-1", "r1").period == "2024-01"

    def test_isolation(self):
        r = AppAPIErrorReport()
        r.generate("inst-1", "r1", "2024-01", [], 100)
        assert r.list_reports("inst-2") == []
