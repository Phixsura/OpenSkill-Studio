from app.services.app_marketplace_extension_platform_changelog import PlatformChangelogService

def test_add():
    svc = PlatformChangelogService()
    svc.add("4.1.0", "New API", "Added REST API v2", "feature")
    svc.add("4.1.0", "Breaking", "Removed v1 endpoints", "breaking")
    assert len(svc.get_by_version("4.1.0")) == 2

def test_breaking():
    svc = PlatformChangelogService()
    svc.add("4.0", "Feature", "New thing", "feature")
    svc.add("4.0", "Break", "Old removed", "breaking")
    assert len(svc.get_breaking()) == 1
