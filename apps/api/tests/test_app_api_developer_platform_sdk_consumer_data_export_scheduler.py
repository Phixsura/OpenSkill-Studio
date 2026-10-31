import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_data_export_scheduler import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler, ExportSchedule,
)

class TestDataExportScheduler:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_list(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler()
        svc.create("inst-1", ExportSchedule(schedule_id="s1", consumer_id="c1", data_type="logs", format="csv", frequency="daily"))
        schedules = svc.list_schedules("inst-1", "c1")
        assert len(schedules) == 1 and schedules[0].frequency == "daily"

    def test_enabled_filter(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler()
        svc.create("inst-1", ExportSchedule(schedule_id="s1", consumer_id="c1", data_type="logs", enabled=True))
        svc.create("inst-1", ExportSchedule(schedule_id="s2", consumer_id="c1", data_type="analytics", enabled=False))
        assert len(svc.list_schedules("inst-1", "c1", enabled_only=True)) == 1

    def test_update(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler()
        svc.create("inst-1", ExportSchedule(schedule_id="s1", consumer_id="c1", data_type="usage", frequency="daily"))
        svc.update("inst-1", "c1", "s1", frequency="weekly")
        assert svc.list_schedules("inst-1", "c1")[0].frequency == "weekly"

    def test_mark_run(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler()
        svc.create("inst-1", ExportSchedule(schedule_id="s1", consumer_id="c1", data_type="logs"))
        svc.mark_run("inst-1", "c1", "s1", self._now())
        assert svc.list_schedules("inst-1", "c1")[0].last_run_at == self._now()

    def test_delete(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler()
        svc.create("inst-1", ExportSchedule(schedule_id="s1", consumer_id="c1", data_type="logs"))
        svc.delete("inst-1", "c1", "s1")
        assert len(svc.list_schedules("inst-1", "c1")) == 0

    def test_invalid_data_type(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler()
        with pytest.raises(ValueError, match="Invalid data_type"):
            svc.create("inst-1", ExportSchedule(schedule_id="s1", consumer_id="c1", data_type="unknown"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler()
        svc.create("inst-1", ExportSchedule(schedule_id="s1", consumer_id="c1", data_type="logs"))
        assert len(svc.list_schedules("inst-2", "c1")) == 0
