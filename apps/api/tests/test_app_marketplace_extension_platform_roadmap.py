from app.services.app_marketplace_extension_platform_roadmap import PlatformRoadmapService

def test_add_and_vote():
    svc = PlatformRoadmapService()
    svc.add("r1", "Dark Mode", "Add dark theme", "ui")
    assert svc.vote("r1") == 1
    assert svc.vote("r1") == 2

def test_by_status():
    svc = PlatformRoadmapService()
    svc.add("r1", "A", "d", "ui", "planned")
    svc.add("r2", "B", "d", "api", "in_progress")
    svc.add("r3", "C", "d", "ui", "planned")
    assert len(svc.get_by_status("planned")) == 2

def test_stats():
    svc = PlatformRoadmapService()
    svc.add("r1", "A", "d", "ui", "planned")
    svc.add("r2", "B", "d", "api", "completed")
    svc.vote("r1"); svc.vote("r1")
    stats = svc.get_stats()
    assert stats["total"] == 2
    assert stats["total_votes"] == 2
