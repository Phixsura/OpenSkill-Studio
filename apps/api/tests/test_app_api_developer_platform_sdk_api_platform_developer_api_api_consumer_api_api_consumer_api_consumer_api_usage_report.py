import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_usage_report import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport, UsageReport, UsageMetric,
)

class TestConsumerApiUsageReport:
    def _now(self):
        return datetime(2026, 6, 1)

    def _report(self, rid="r1", period="2026-06"):
        return UsageReport(report_id=rid, consumer_id="c1", period=period, generated_at=self._now(),
            metrics=[UsageMetric(metric="api_calls", value=10000, unit="requests", change_pct=15.0)], total_cost_cents=4999)

    def test_generate_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport()
        svc.generate("inst-1", self._report())
        report = svc.get_report("inst-1", "r1")
        assert report.period == "2026-06" and len(report.metrics) == 1

    def test_lifecycle(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport()
        svc.generate("inst-1", self._report())
        svc.mark_delivered("inst-1", "r1")
        assert svc.get_report("inst-1", "r1").status == "delivered"
        svc.acknowledge("inst-1", "r1")
        assert svc.get_report("inst-1", "r1").status == "acknowledged"

    def test_total_cost(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport()
        svc.generate("inst-1", self._report("r1", "2026-05"))
        svc.generate("inst-1", self._report("r2", "2026-06"))
        assert svc.total_cost("inst-1", "c1") == 9998

    def test_empty_metrics_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport()
        with pytest.raises(ValueError, match="at least one metric"):
            svc.generate("inst-1", UsageReport(report_id="r1", consumer_id="c1", period="2026-06", generated_at=self._now()))

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport()
        svc.generate("inst-1", self._report())
        with pytest.raises(ValueError, match="already exists"):
            svc.generate("inst-1", self._report())

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport()
        svc.generate("inst-1", self._report())
        assert svc.get_report("inst-2", "r1") is None
