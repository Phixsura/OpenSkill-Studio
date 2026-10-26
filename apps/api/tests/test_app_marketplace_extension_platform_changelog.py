from app.services.app_marketplace_extension_platform_changelog import PlatformChangelogService


def test_add_and_latest():
    svc = PlatformChangelogService()
    svc.add_release("1.0", "2024-01-01", "Initial Release", features=["Core platform"])
    svc.add_release("2.0", "2024-06-01", "Major Update", features=["SDK", "Sandbox"])
    latest = svc.get_latest()
    assert latest.version == "2.0"


def test_breaking_changes():
    svc = PlatformChangelogService()
    svc.add_release("2.0", "2024-06-01", "V2", breaking=["New API format", "Auth change"])
    svc.add_release("1.0", "2024-01-01", "V1")
    breaking = svc.get_breaking_changes()
    assert len(breaking) == 2


def test_search():
    svc = PlatformChangelogService()
    svc.add_release("1.0", "2024-01-01", "Launch", features=["Sandbox runtime"])
    svc.add_release("1.1", "2024-02-01", "Patch", fixes=["Webhook timeout"])
    results = svc.search("sandbox")
    assert len(results) == 1


def test_stats():
    svc = PlatformChangelogService()
    svc.add_release("1.0", "d", "T", features=["a", "b"], fixes=["c"], breaking=["d"])
    stats = svc.get_stats()
    assert stats["total_features"] == 2
    assert stats["total_breaking"] == 1
