from app.services.app_api_developer_api_performance_overview import AppAPIDeveloperAPIPerformanceOverview

class TestPerfOverview:
    def test_grade_a(self):
        p = AppAPIDeveloperAPIPerformanceOverview()
        po = p.update("inst-1", p99_ms=150, error_rate=0.5)
        assert po.performance_grade == "A"

    def test_grade_d(self):
        p = AppAPIDeveloperAPIPerformanceOverview()
        po = p.update("inst-1", p99_ms=2000, error_rate=10)
        assert po.performance_grade == "D"

    def test_isolation(self):
        p = AppAPIDeveloperAPIPerformanceOverview()
        p.update("inst-1", avg_latency_ms=50)
        assert p.get("inst-2").avg_latency_ms == 0.0
