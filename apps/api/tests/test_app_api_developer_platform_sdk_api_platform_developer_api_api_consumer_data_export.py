import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_data_export import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDataExport, ExportJob, ExportFormat, ExportStatus,
)

class TestConsumerDataExport:
    def test_create_and_complete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDataExport()
        job = svc.create_export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format=ExportFormat.JSON, data_types=["usage", "billing"]))
        assert job.status == ExportStatus.PENDING
        job = svc.complete_export("inst-1", "j1", 5000, 1024000)
        assert job.status == ExportStatus.COMPLETED
        assert job.record_count == 5000

    def test_invalid_data_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDataExport()
        with pytest.raises(ValueError, match="Invalid data types"):
            svc.create_export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format=ExportFormat.CSV, data_types=["invalid"]))

    def test_fail_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDataExport()
        svc.create_export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format=ExportFormat.JSON, data_types=["logs"]))
        job = svc.fail_export("inst-1", "j1")
        assert job.status == ExportStatus.FAILED

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDataExport()
        svc.create_export("inst-1", ExportJob(job_id="j1", consumer_id="c1", format=ExportFormat.JSON, data_types=["usage"]))
        assert len(svc.list_exports("inst-2")) == 0
