from app.services.app_api_developer_api_complete_overview import AppAPIDeveloperAPICompleteOverview

class TestCompleteOverview:
    def test_update(self):
        o = AppAPIDeveloperAPICompleteOverview()
        co = o.update("inst-1",
            total_services=388, total_endpoints=1500, total_developers=1000,
            api_health_grade="A", avg_latency_ms=45, uptime_pct=99.99,
            webhook_success_rate=99.8, webhook_destinations=50,
            developer_satisfaction_nps=75, onboarding_completion_pct=92,
            security_score=98, open_findings=0,
            documentation_coverage_pct=95, platform_grade="A"
        )
        assert co.total_services == 388
        assert co.platform_grade == "A"

    def test_default(self):
        o = AppAPIDeveloperAPICompleteOverview()
        assert o.get("inst-1").uptime_pct == 100.0

    def test_isolation(self):
        o = AppAPIDeveloperAPICompleteOverview()
        o.update("inst-1", total_services=100)
        assert o.get("inst-2").total_services == 0
