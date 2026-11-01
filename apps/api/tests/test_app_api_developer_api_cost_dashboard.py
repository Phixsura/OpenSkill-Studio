from app.services.app_api_developer_api_cost_dashboard import AppAPIDeveloperAPICostDashboard

class TestCostDashboard:
    def test_update(self):
        d = AppAPIDeveloperAPICostDashboard()
        cd = d.update("inst-1", total_cost=1500.0, budget_limit=2000.0, projected_monthly=1800.0)
        assert cd.over_budget is False

    def test_over_budget(self):
        d = AppAPIDeveloperAPICostDashboard()
        cd = d.update("inst-1", total_cost=2500.0, budget_limit=2000.0)
        assert cd.over_budget is True

    def test_isolation(self):
        d = AppAPIDeveloperAPICostDashboard()
        d.update("inst-1", total_cost=1000)
        assert d.get("inst-2").total_cost == 0.0
