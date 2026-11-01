from app.services.app_api_developer_api_api_developer_api_api_platform_capacity_planner import AppAPIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlanner

class TestCapacityPlanner:
    def test_plan(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlanner()
        c = p.plan("inst-1", "api_capacity", 50000, 100000, 10, "rps")
        assert c.utilization_pct == 50.0

    def test_months_until_full(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlanner()
        c = p.plan("inst-1", "storage", 500, 1000, 20, "GB")
        assert c.months_until_full == 5.0  # 500 remaining / (500 * 0.2) = 5

    def test_needs_scaling_utilization(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlanner()
        p.plan("inst-1", "compute", 80, 100, 5, "cores")
        assert len(p.needs_scaling("inst-1")) == 1

    def test_needs_scaling_growth(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlanner()
        p.plan("inst-1", "api", 60, 100, 50, "rps")
        c = p.all_plans("inst-1")[0]
        assert c.months_until_full < 3
        assert c.needs_scaling is True

    def test_isolation(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlanner()
        p.plan("inst-1", "api", 50, 100, 10)
        assert len(p.all_plans("inst-2")) == 0
