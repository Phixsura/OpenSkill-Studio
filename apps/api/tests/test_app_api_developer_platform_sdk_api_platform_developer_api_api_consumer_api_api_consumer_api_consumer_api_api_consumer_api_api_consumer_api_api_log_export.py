import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_log_export import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport, LogEntry, ExportJob,
)

class TestConsumerApiLogExport:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_json_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport()
        svc.append_log("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/api", status_code=200, latency_ms=50, timestamp=self._now()))
        job = svc.export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format="json", start_time=self._now() - timedelta(hours=1), end_time=self._now() + timedelta(hours=1)))
        assert job.record_count == 1 and job.status == "completed" and '"GET"' in job.content

    def test_csv_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport()
        svc.append_log("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="POST", path="/api", status_code=201, latency_ms=30, timestamp=self._now()))
        job = svc.export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format="csv", start_time=self._now() - timedelta(hours=1), end_time=self._now() + timedelta(hours=1)))
        assert "method" in job.content and "POST" in job.content

    def test_ndjson_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport()
        svc.append_log("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/a", status_code=200, latency_ms=10, timestamp=self._now()))
        svc.append_log("inst-1", LogEntry(log_id="l2", consumer_id="c1", method="GET", path="/b", status_code=200, latency_ms=20, timestamp=self._now()))
        job = svc.export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format="ndjson", start_time=self._now() - timedelta(hours=1), end_time=self._now() + timedelta(hours=1)))
        assert job.content.count("\n") == 1  # 2 records, 1 newline separator

    def test_time_filter(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport()
        svc.append_log("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/", status_code=200, latency_ms=10, timestamp=self._now()))
        svc.append_log("inst-1", LogEntry(log_id="l2", consumer_id="c1", method="GET", path="/", status_code=200, latency_ms=10, timestamp=self._now() + timedelta(hours=5)))
        job = svc.export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format="json", start_time=self._now(), end_time=self._now() + timedelta(hours=1)))
        assert job.record_count == 1

    def test_invalid_format(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport()
        with pytest.raises(ValueError, match="Unsupported"):
            svc.export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format="xml", start_time=self._now(), end_time=self._now()))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiLogExport()
        svc.append_log("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/", status_code=200, latency_ms=10, timestamp=self._now()))
        job = svc.export("inst-2", ExportJob(job_id="j1", consumer_id="c1", format="json", start_time=self._now() - timedelta(hours=1), end_time=self._now() + timedelta(hours=1)))
        assert job.record_count == 0
