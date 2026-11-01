from app.services.app_api_developer_api_final_dashboard import AppAPIDeveloperAPIFinalDashboard

class TestFinalDashboard:
    def test_all_a(self):
        d = AppAPIDeveloperAPIFinalDashboard()
        fd = d.update("inst-1")
        assert fd.overall_grade == "A"

    def test_mixed(self):
        d = AppAPIDeveloperAPIFinalDashboard()
        fd = d.update("inst-1", platform_health_grade="A", api_performance_grade="B", webhook_delivery_grade="A", developer_experience_grade="C", documentation_grade="B", security_grade="A")
        assert fd.overall_grade == "B"

    def test_metrics(self):
        d = AppAPIDeveloperAPIFinalDashboard()
        fd = d.update("inst-1", total_developers=500, total_api_calls=10000000, overall_uptime=99.99, nps_score=70)
        assert fd.total_developers == 500

    def test_isolation(self):
        d = AppAPIDeveloperAPIFinalDashboard()
        d.update("inst-1", total_developers=100)
        assert d.get("inst-2").total_developers == 0
