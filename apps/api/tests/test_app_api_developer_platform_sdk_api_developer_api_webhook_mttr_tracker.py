from app.services.app_api_developer_platform_sdk_api_developer_api_webhook_mttr_tracker import AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTracker

class TestWebhookMTTRTracker:
    def test_failure_and_recovery(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTracker()
        t.record_failure("inst-1", "i1", "https://a.com")
        r = t.record_recovery("inst-1", "i1")
        assert r.recovered_at is not None
        assert r.recovery_time_seconds is not None

    def test_mttr(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTracker()
        t.record_failure("inst-1", "i1", "https://a.com")
        t.record_recovery("inst-1", "i1")
        assert t.mttr_seconds("inst-1") >= 0

    def test_open_incidents(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTracker()
        t.record_failure("inst-1", "i1", "https://a.com")
        t.record_failure("inst-1", "i2", "https://b.com")
        t.record_recovery("inst-1", "i1")
        assert len(t.open_incidents("inst-1")) == 1

    def test_isolation(self):
        t = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTracker()
        t.record_failure("inst-1", "i1", "https://a.com")
        assert t.total_incidents("inst-2") == 0
