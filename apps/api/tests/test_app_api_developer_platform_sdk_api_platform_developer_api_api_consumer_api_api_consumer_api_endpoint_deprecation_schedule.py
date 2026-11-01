import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_deprecation_schedule import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule, DeprecationEntry,
)

class TestEndpointDeprecationSchedule:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_schedule_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule()
        entry = DeprecationEntry(endpoint_id="e1", path="/api/v1/users", deprecated_at=self._now() + timedelta(days=30), sunset_at=self._now() + timedelta(days=90), replacement_path="/api/v2/users")
        svc.schedule("inst-1", entry)
        got = svc.get("inst-1", "e1")
        assert got.path == "/api/v1/users"
        assert got.replacement_path == "/api/v2/users"

    def test_effective_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule()
        entry = DeprecationEntry(endpoint_id="e1", path="/old", deprecated_at=self._now(), sunset_at=self._now() + timedelta(days=60))
        svc.schedule("inst-1", entry)
        assert entry.effective_status(self._now() - timedelta(days=1)) == "active"
        assert entry.effective_status(self._now()) == "deprecated"
        assert entry.effective_status(self._now() + timedelta(days=60)) == "sunset"

    def test_list_deprecated(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule()
        svc.schedule("inst-1", DeprecationEntry(endpoint_id="e1", path="/a", deprecated_at=self._now(), sunset_at=self._now() + timedelta(days=90)))
        svc.schedule("inst-1", DeprecationEntry(endpoint_id="e2", path="/b", deprecated_at=self._now() + timedelta(days=60), sunset_at=self._now() + timedelta(days=120)))
        deps = svc.list_deprecated("inst-1", self._now() + timedelta(days=1))
        assert len(deps) == 1 and deps[0].endpoint_id == "e1"

    def test_upcoming(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule()
        svc.schedule("inst-1", DeprecationEntry(endpoint_id="e1", path="/soon", deprecated_at=self._now() + timedelta(days=10), sunset_at=self._now() + timedelta(days=60)))
        svc.schedule("inst-1", DeprecationEntry(endpoint_id="e2", path="/later", deprecated_at=self._now() + timedelta(days=90), sunset_at=self._now() + timedelta(days=180)))
        upcoming = svc.upcoming("inst-1", self._now(), within_days=30)
        assert len(upcoming) == 1 and upcoming[0].endpoint_id == "e1"

    def test_invalid_dates(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule()
        with pytest.raises(ValueError, match="sunset_at must be after"):
            svc.schedule("inst-1", DeprecationEntry(endpoint_id="e1", path="/x", deprecated_at=self._now(), sunset_at=self._now()))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule()
        svc.schedule("inst-1", DeprecationEntry(endpoint_id="e1", path="/x", deprecated_at=self._now(), sunset_at=self._now() + timedelta(days=30)))
        assert len(svc.list_all("inst-2")) == 0
