from app.services.app_api_developer_api_tenant_usage_report import AppAPIDeveloperAPITenantUsageReport

class TestTenantUsageReport:
    def test_record(self):
        r = AppAPIDeveloperAPITenantUsageReport()
        u = r.record("inst-1", "t1", api_calls=1000, webhook_deliveries=500)
        assert u.api_calls == 1000

    def test_accumulate(self):
        r = AppAPIDeveloperAPITenantUsageReport()
        r.record("inst-1", "t1", api_calls=100)
        r.record("inst-1", "t1", api_calls=200)
        assert r.get("inst-1", "t1").api_calls == 300

    def test_top_tenants(self):
        r = AppAPIDeveloperAPITenantUsageReport()
        r.record("inst-1", "t1", api_calls=100)
        r.record("inst-1", "t2", api_calls=500)
        top = r.top_tenants("inst-1", by="api_calls", limit=1)
        assert top[0].tenant_id == "t2"

    def test_cost(self):
        r = AppAPIDeveloperAPITenantUsageReport()
        r.record("inst-1", "t1", api_calls=10000)
        assert r.get("inst-1", "t1").total_cost_cents == 10

    def test_isolation(self):
        r = AppAPIDeveloperAPITenantUsageReport()
        r.record("inst-1", "t1", api_calls=100)
        assert r.total_cost_cents("inst-2") == 0
