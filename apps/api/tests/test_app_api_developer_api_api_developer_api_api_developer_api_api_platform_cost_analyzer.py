import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_platform_cost_analyzer import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzer

class TestPlatformCostAnalyzer:
    def test_record(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzer()
        r = a.record("inst-1", "2025-01", [
            {"dimension": "compute", "cost_cents": 50000, "usage": 100, "unit": "cpu-hours"},
            {"dimension": "api_calls", "cost_cents": 30000, "usage": 1000000, "unit": "requests"},
        ])
        assert r.total_cents == 80000
        assert r.top_cost_dimension == "compute"

    def test_invalid_dimension(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzer()
        with pytest.raises(ValueError):
            a.record("inst-1", "2025-01", [{"dimension": "unknown"}])

    def test_trend(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzer()
        a.record("inst-1", "2025-02", [{"dimension": "compute", "cost_cents": 60000}])
        a.record("inst-1", "2025-01", [{"dimension": "compute", "cost_cents": 50000}])
        trend = a.trend("inst-1")
        assert trend[0].period == "2025-01"

    def test_total_spend(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzer()
        a.record("inst-1", "2025-01", [{"dimension": "compute", "cost_cents": 50000}])
        a.record("inst-1", "2025-02", [{"dimension": "compute", "cost_cents": 60000}])
        assert a.total_spend_cents("inst-1") == 110000

    def test_isolation(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzer()
        a.record("inst-1", "2025-01", [{"dimension": "compute", "cost_cents": 50000}])
        assert a.total_spend_cents("inst-2") == 0
