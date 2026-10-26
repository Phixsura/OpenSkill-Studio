from app.services.app_marketplace_extension_install_analytics import (
    InstallAnalyticsService, InstallAction,
)


def test_track_install():
    svc = InstallAnalyticsService()
    svc.track("ext-1", "u1", InstallAction.INSTALL, "1.0.0", source="marketplace")
    assert svc.get_active_installs("ext-1") == 1


def test_track_uninstall():
    svc = InstallAnalyticsService()
    svc.track("ext-1", "u1", InstallAction.INSTALL, "1.0.0")
    svc.track("ext-1", "u1", InstallAction.UNINSTALL, "1.0.0")
    assert svc.get_active_installs("ext-1") == 0


def test_install_stats():
    svc = InstallAnalyticsService()
    svc.track("ext-1", "u1", InstallAction.INSTALL, "1.0.0")
    svc.track("ext-1", "u2", InstallAction.INSTALL, "1.0.0")
    svc.track("ext-1", "u3", InstallAction.INSTALL, "1.0.0")
    svc.track("ext-1", "u1", InstallAction.UNINSTALL, "1.0.0")
    stats = svc.get_install_stats("ext-1")
    assert stats["total_installs"] == 3
    assert stats["total_uninstalls"] == 1
    assert stats["active_installs"] == 2
    assert stats["retention_rate"] == 66.7


def test_source_breakdown():
    svc = InstallAnalyticsService()
    svc.track("ext-1", "u1", InstallAction.INSTALL, source="marketplace")
    svc.track("ext-1", "u2", InstallAction.INSTALL, source="marketplace")
    svc.track("ext-1", "u3", InstallAction.INSTALL, source="cli")
    breakdown = svc.get_source_breakdown("ext-1")
    assert breakdown["marketplace"] == 2
    assert breakdown["cli"] == 1


def test_region_breakdown():
    svc = InstallAnalyticsService()
    svc.track("ext-1", "u1", InstallAction.INSTALL, region="US")
    svc.track("ext-1", "u2", InstallAction.INSTALL, region="EU")
    svc.track("ext-1", "u3", InstallAction.INSTALL, region="US")
    regions = svc.get_region_breakdown("ext-1")
    assert regions["US"] == 2


def test_version_adoption():
    svc = InstallAnalyticsService()
    svc.track("ext-1", "u1", InstallAction.INSTALL, "1.0.0")
    svc.track("ext-1", "u2", InstallAction.INSTALL, "1.0.0")
    svc.track("ext-1", "u1", InstallAction.UPDATE, "2.0.0")
    adoption = svc.get_version_adoption("ext-1")
    assert adoption["2.0.0"] == 1
    assert adoption["1.0.0"] == 1


def test_churn_rate():
    svc = InstallAnalyticsService()
    for i in range(10):
        svc.track("ext-1", f"u{i}", InstallAction.INSTALL)
    for i in range(3):
        svc.track("ext-1", f"u{i}", InstallAction.UNINSTALL)
    assert svc.get_churn_rate("ext-1") == 30.0
