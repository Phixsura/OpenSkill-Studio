from app.services.app_marketplace_complete_platform_overview import build_complete_platform_overview

def test_overview():
    p = build_complete_platform_overview(
        platform_stats={"total_apps": 500, "total_developers": 100, "total_installs": 25000, "monthly_published": 15},
        trending_apps=[{"name": "App1"}], recent_updates=[{"title": "v2.0"}],
        top_developers=[{"name": "DevCo"}], categories=[{"key": "connector"}],
        announcements=[{"title": "New API v3"}])
    assert p["page_type"] == "platform_overview"
    assert p["stats"]["total_apps"] == 500
    assert len(p["sections"]) == 5
    assert p["links"]["docs"] == "/docs/developer"

def test_empty():
    p = build_complete_platform_overview(
        platform_stats={}, trending_apps=[], recent_updates=[],
        top_developers=[], categories=[], announcements=[])
    assert p["stats"]["total_apps"] == 0
