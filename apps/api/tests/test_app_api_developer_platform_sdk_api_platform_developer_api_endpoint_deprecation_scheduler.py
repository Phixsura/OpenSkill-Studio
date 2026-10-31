import pytest, time
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_endpoint_deprecation_scheduler import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationScheduler, DeprecationPhase,
)

class TestEndpointDeprecationScheduler:
    def test_schedule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationScheduler()
        ds = svc.schedule("inst-1", "/api/v1/old", "GET", sunset_at=time.time() + 86400, replacement="/api/v2/new")
        assert ds.phase == DeprecationPhase.ANNOUNCED
        assert ds.replacement == "/api/v2/new"

    def test_advance_phase(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationScheduler()
        svc.schedule("inst-1", "/old", "GET", sunset_at=time.time() + 86400)
        svc.advance_phase("inst-1", "/old", "GET", DeprecationPhase.WARNING)
        ds = svc._get("inst-1", "/old", "GET")
        assert ds.phase == DeprecationPhase.WARNING

    def test_cannot_go_backwards(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationScheduler()
        svc.schedule("inst-1", "/old", "GET", sunset_at=time.time() + 86400)
        svc.advance_phase("inst-1", "/old", "GET", DeprecationPhase.WARNING)
        with pytest.raises(ValueError, match="Cannot move"):
            svc.advance_phase("inst-1", "/old", "GET", DeprecationPhase.ANNOUNCED)

    def test_overdue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationScheduler()
        svc.schedule("inst-1", "/old", "GET", sunset_at=time.time() + 86400)
        # manually set sunset in the past
        ds = svc._get("inst-1", "/old", "GET")
        ds.sunset_at = time.time() - 1
        assert len(svc.overdue("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationScheduler()
        svc.schedule("inst-1", "/old", "GET", sunset_at=time.time() + 86400)
        assert len(svc.list_schedules("inst-2")) == 0
