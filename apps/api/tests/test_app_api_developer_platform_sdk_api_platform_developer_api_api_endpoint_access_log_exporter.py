import json
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_endpoint_access_log_exporter import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporter, AccessLogEntry, ExportConfig,
)

class TestAccessLogExporter:
    def test_record_and_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporter()
        svc.record("inst-1", AccessLogEntry(timestamp=1000, method="GET", path="/users", status_code=200, duration_ms=50, consumer_id="c1"))
        data = json.loads(svc.export_json("inst-1"))
        assert len(data) == 1 and data[0]["method"] == "GET"

    def test_ip_excluded_by_default(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporter()
        svc.record("inst-1", AccessLogEntry(timestamp=1000, method="GET", path="/a", status_code=200, duration_ms=10, ip_address="1.2.3.4"))
        data = json.loads(svc.export_json("inst-1"))
        assert "ip" not in data[0]

    def test_ip_included_when_configured(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporter()
        svc.record("inst-1", AccessLogEntry(timestamp=1000, method="GET", path="/a", status_code=200, duration_ms=10, ip_address="1.2.3.4"))
        data = json.loads(svc.export_json("inst-1", ExportConfig(include_ip=True)))
        assert data[0]["ip"] == "1.2.3.4"

    def test_by_status_range(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporter()
        svc.record("inst-1", AccessLogEntry(timestamp=1, method="GET", path="/a", status_code=200, duration_ms=10))
        svc.record("inst-1", AccessLogEntry(timestamp=2, method="GET", path="/a", status_code=500, duration_ms=10))
        ranges = svc.by_status_range("inst-1")
        assert ranges["2xx"] == 1 and ranges["5xx"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporter()
        svc.record("inst-1", AccessLogEntry(timestamp=1, method="GET", path="/a", status_code=200, duration_ms=10))
        assert svc.entry_count("inst-2") == 0
