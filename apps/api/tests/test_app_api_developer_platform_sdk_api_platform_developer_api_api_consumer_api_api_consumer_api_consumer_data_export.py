import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_data_export import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport, ExportRequest,
)

class TestConsumerDataExport:
    def test_json_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport()
        svc.create_export("inst-1", ExportRequest(export_id="ex1", consumer_id="c1", format="json"))
        result = svc.execute("inst-1", "ex1", [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
        assert result.record_count == 2 and result.format == "json"
        assert '"Alice"' in result.content

    def test_csv_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport()
        svc.create_export("inst-1", ExportRequest(export_id="ex1", consumer_id="c1", format="csv"))
        result = svc.execute("inst-1", "ex1", [{"id": "1", "name": "Alice"}])
        assert "id,name" in result.content and "Alice" in result.content

    def test_ndjson_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport()
        svc.create_export("inst-1", ExportRequest(export_id="ex1", consumer_id="c1", format="ndjson"))
        result = svc.execute("inst-1", "ex1", [{"a": 1}, {"a": 2}])
        lines = result.content.strip().split("\n")
        assert len(lines) == 2

    def test_filter(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport()
        svc.create_export("inst-1", ExportRequest(export_id="ex1", consumer_id="c1", format="json", filters={"status": "active"}))
        result = svc.execute("inst-1", "ex1", [{"id": "1", "status": "active"}, {"id": "2", "status": "inactive"}])
        assert result.record_count == 1

    def test_invalid_format(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport()
        with pytest.raises(ValueError, match="Unsupported format"):
            svc.create_export("inst-1", ExportRequest(export_id="ex1", consumer_id="c1", format="xml"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExport()
        svc.create_export("inst-1", ExportRequest(export_id="ex1", consumer_id="c1"))
        assert svc.get_status("inst-2", "ex1") is None
