import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_maintenance_window import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow, MaintenanceWindow,
)

class TestEndpointMaintenanceWindow:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_schedule_and_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow()
        svc.schedule("inst-1", MaintenanceWindow(window_id="w1", endpoint_path="/api", starts_at=self._now(), ends_at=self._now() + timedelta(hours=2), reason="Deploy"))
        maint = svc.is_in_maintenance("inst-1", "/api", self._now() + timedelta(hours=1))
        assert maint is not None and maint.reason == "Deploy"

    def test_not_in_maintenance(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow()
        svc.schedule("inst-1", MaintenanceWindow(window_id="w1", endpoint_path="/api", starts_at=self._now() + timedelta(hours=5), ends_at=self._now() + timedelta(hours=7)))
        assert svc.is_in_maintenance("inst-1", "/api", self._now()) is None

    def test_cancel(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow()
        svc.schedule("inst-1", MaintenanceWindow(window_id="w1", endpoint_path="/api", starts_at=self._now(), ends_at=self._now() + timedelta(hours=2)))
        svc.cancel("inst-1", "w1")
        assert svc.is_in_maintenance("inst-1", "/api", self._now() + timedelta(hours=1)) is None

    def test_update_statuses(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow()
        svc.schedule("inst-1", MaintenanceWindow(window_id="w1", endpoint_path="/api", starts_at=self._now(), ends_at=self._now() + timedelta(hours=1)))
        svc.update_statuses("inst-1", self._now() + timedelta(minutes=30))
        assert svc.list_all("inst-1")[0].status == "active"
        svc.update_statuses("inst-1", self._now() + timedelta(hours=2))
        assert svc.list_all("inst-1")[0].status == "completed"

    def test_invalid_dates(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow()
        with pytest.raises(ValueError, match="ends_at must be after"):
            svc.schedule("inst-1", MaintenanceWindow(window_id="w1", endpoint_path="/api", starts_at=self._now(), ends_at=self._now()))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow()
        svc.schedule("inst-1", MaintenanceWindow(window_id="w1", endpoint_path="/api", starts_at=self._now(), ends_at=self._now() + timedelta(hours=1)))
        assert len(svc.list_all("inst-2")) == 0
