import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_deprecation_notice import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNotice, DeprecationNotice, NoticeUrgency,
)

class TestDeprecationNotice:
    def test_create_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNotice()
        svc.create_notice("inst-1", DeprecationNotice(notice_id="n1", endpoint="/v1/users", method="GET", urgency=NoticeUrgency.WARNING, message="Use /v2/users", sunset_date="2025-06-01", replacement="/v2/users"))
        assert len(svc.list_notices("inst-1")) == 1

    def test_acknowledge(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNotice()
        svc.create_notice("inst-1", DeprecationNotice(notice_id="n1", endpoint="/old", method="GET", urgency=NoticeUrgency.INFO, message="Deprecated", sunset_date="2025-12-31"))
        svc.acknowledge("inst-1", "n1", "c1")
        assert len(svc.unacknowledged_for("inst-1", "c1")) == 0
        assert len(svc.unacknowledged_for("inst-1", "c2")) == 1

    def test_urgent_notices(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNotice()
        svc.create_notice("inst-1", DeprecationNotice(notice_id="n1", endpoint="/a", method="GET", urgency=NoticeUrgency.INFO, message="x", sunset_date="2026-01-01"))
        svc.create_notice("inst-1", DeprecationNotice(notice_id="n2", endpoint="/b", method="POST", urgency=NoticeUrgency.FINAL, message="y", sunset_date="2025-01-01"))
        assert len(svc.urgent_notices("inst-1")) == 1

    def test_duplicate_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNotice()
        svc.create_notice("inst-1", DeprecationNotice(notice_id="n1", endpoint="/a", method="GET", urgency=NoticeUrgency.INFO, message="x", sunset_date="2026-01-01"))
        with pytest.raises(ValueError, match="exists"):
            svc.create_notice("inst-1", DeprecationNotice(notice_id="n1", endpoint="/a", method="GET", urgency=NoticeUrgency.INFO, message="x", sunset_date="2026-01-01"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNotice()
        svc.create_notice("inst-1", DeprecationNotice(notice_id="n1", endpoint="/a", method="GET", urgency=NoticeUrgency.INFO, message="x", sunset_date="2026-01-01"))
        assert len(svc.list_notices("inst-2")) == 0
