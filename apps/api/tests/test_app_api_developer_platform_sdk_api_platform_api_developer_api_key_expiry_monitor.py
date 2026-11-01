import time
from app.services.app_api_developer_platform_sdk_api_platform_api_developer_api_key_expiry_monitor import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitor

class TestKeyExpiryMonitor:
    def test_track(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitor()
        k = m.track("inst-1", "k1", "c1", time.time() + 86400 * 90)
        assert k.urgency == "ok"
        assert k.days_until_expiry > 89

    def test_expiring_soon(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitor()
        m.track("inst-1", "k1", "c1", time.time() + 86400 * 10)
        m.track("inst-1", "k2", "c2", time.time() + 86400 * 90)
        assert len(m.expiring_soon("inst-1", 30)) == 1

    def test_expired(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitor()
        m.track("inst-1", "k1", "c1", time.time() - 86400)
        assert len(m.expired_keys("inst-1")) == 1
        assert m.all_keys("inst-1")[0].urgency == "expired"

    def test_critical(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitor()
        k = m.track("inst-1", "k1", "c1", time.time() + 86400 * 3)
        assert k.urgency == "critical"

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitor()
        m.track("inst-1", "k1", "c1", time.time() + 86400)
        assert len(m.all_keys("inst-2")) == 0
