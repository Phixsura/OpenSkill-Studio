from app.services.app_api_developer_api_api_developer_api_api_consumer_quota_usage_report import AppAPIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReport

class TestQuotaUsageReport:
    def test_record(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReport()
        e = r.record("inst-1", "c1", "2025-01", api_calls_used=5000, api_calls_limit=10000)
        assert e.api_usage_pct == 50.0

    def test_over_limit(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReport()
        r.record("inst-1", "c1", "2025-01", api_calls_used=15000, api_calls_limit=10000)
        r.record("inst-1", "c2", "2025-01", api_calls_used=5000, api_calls_limit=10000)
        assert len(r.over_limit("inst-1", "2025-01")) == 1

    def test_by_consumer(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReport()
        r.record("inst-1", "c1", "2025-01", api_calls_used=1000, api_calls_limit=10000)
        r.record("inst-1", "c1", "2025-02", api_calls_used=2000, api_calls_limit=10000)
        assert len(r.by_consumer("inst-1", "c1")) == 2

    def test_storage_over(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReport()
        e = r.record("inst-1", "c1", "2025-01", storage_used_mb=150.0, storage_limit_mb=100.0)
        assert e.any_over_limit is True

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReport()
        r.record("inst-1", "c1", "2025-01", api_calls_used=1000, api_calls_limit=10000)
        assert len(r.all_reports("inst-2", "2025-01")) == 0
