from app.services.app_api_developer_api_api_webhook_connection_pool import AppAPIDeveloperAPIApiWebhookConnectionPool

class TestConnectionPool:
    def test_configure(self):
        p = AppAPIDeveloperAPIApiWebhookConnectionPool()
        s = p.configure("inst-1", "https://a.com", 50)
        assert s.max_connections == 50

    def test_utilization(self):
        p = AppAPIDeveloperAPIApiWebhookConnectionPool()
        p.configure("inst-1", "https://a.com", 100)
        p.update("inst-1", "https://a.com", active=75, idle=25)
        pool = p.all_pools("inst-1")[0]
        assert pool.utilization_pct == 75.0

    def test_unhealthy_high_util(self):
        p = AppAPIDeveloperAPIApiWebhookConnectionPool()
        p.configure("inst-1", "https://a.com", 10)
        p.update("inst-1", "https://a.com", active=9, idle=1)
        assert len(p.unhealthy("inst-1")) == 1

    def test_unhealthy_errors(self):
        p = AppAPIDeveloperAPIApiWebhookConnectionPool()
        p.configure("inst-1", "https://a.com", 100)
        p.update("inst-1", "https://a.com", active=10, idle=90, errors=5)
        assert len(p.unhealthy("inst-1")) == 1

    def test_isolation(self):
        p = AppAPIDeveloperAPIApiWebhookConnectionPool()
        p.configure("inst-1", "https://a.com", 50)
        assert p.total_active("inst-2") == 0
