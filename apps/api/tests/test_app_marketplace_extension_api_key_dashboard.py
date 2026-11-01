from app.services.app_marketplace_extension_api_key_dashboard import (
    ExtensionApiKeyDashboardService,
)
import time


def test_overview():
    svc = ExtensionApiKeyDashboardService()
    svc.add_key("k1", "ext-1", "prod", "active", usage_count=500)
    svc.add_key("k2", "ext-1", "old", "expired")
    svc.add_key("k3", "ext-2", "test", "active", usage_count=0)
    overview = svc.get_overview()
    assert overview["active"] == 2
    assert overview["expired"] == 1
    assert overview["unused"] == 1
    assert overview["total_usage"] == 500


def test_expiring_soon():
    svc = ExtensionApiKeyDashboardService()
    svc.add_key("k1", "ext-1", "soon", "active",
                expires_at=time.time() + 86400 * 2)  # 2 days
    svc.add_key("k2", "ext-1", "later", "active",
                expires_at=time.time() + 86400 * 30)  # 30 days
    expiring = svc.get_expiring(7)
    assert len(expiring) == 1
    assert expiring[0].name == "soon"


def test_security_alerts():
    svc = ExtensionApiKeyDashboardService()
    svc.add_key("k1", "ext-1", "expiring", "active", usage_count=10,
                expires_at=time.time() + 86400 * 1)
    svc.add_key("k2", "ext-1", "unused", "active", usage_count=0)
    alerts = svc.get_security_alerts()
    assert len(alerts) == 2


def test_by_extension():
    svc = ExtensionApiKeyDashboardService()
    svc.add_key("k1", "ext-1", "a", "active")
    svc.add_key("k2", "ext-2", "b", "active")
    assert len(svc.get_by_extension("ext-1")) == 1
