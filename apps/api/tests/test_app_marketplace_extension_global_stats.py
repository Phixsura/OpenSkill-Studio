from app.services.app_marketplace_extension_global_stats import ExtensionGlobalStatsService


def test_update_and_get():
    svc = ExtensionGlobalStatsService()
    svc.update(total_extensions=553, total_developers=2000, total_tests=2750)
    stats = svc.get_stats()
    assert stats["extensions"] == 553
    assert stats["tests"] == 2750


def test_increment():
    svc = ExtensionGlobalStatsService()
    svc.update(total_installs=1000)
    new_val = svc.increment("total_installs", 500)
    assert new_val == 1500


def test_highlights():
    svc = ExtensionGlobalStatsService()
    svc.update(total_extensions=553, total_tests=2750, total_commits=4821,
               uptime_percent=99.99)
    highlights = svc.get_highlights()
    assert any(h["label"] == "500+ Extensions" for h in highlights)
    assert any(h["label"] == "2000+ Tests GREEN" for h in highlights)
    assert any("4821" in h["label"] for h in highlights)


def test_default_uptime():
    svc = ExtensionGlobalStatsService()
    stats = svc.get_stats()
    assert stats["uptime"] == 99.99
