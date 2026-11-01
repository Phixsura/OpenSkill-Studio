from app.services.app_marketplace_app_app_app_app_app_app_app_platform_changelog import aggregate_changelog

def test_changelog():
    services = [
        {"name": "API", "entries": [
            {"type": "feat", "title": "New endpoint", "date": "2026-10-24", "version": "3.2"},
            {"type": "fix", "title": "Auth bug", "date": "2026-10-23", "version": "3.1.1"},
        ]},
        {"name": "Dashboard", "entries": [
            {"type": "feat", "title": "Dark mode", "date": "2026-10-24", "version": "2.0"},
        ]},
    ]
    r = aggregate_changelog(services)
    assert r["total"] == 3
    assert r["services_count"] == 2
    assert r["by_type"]["feat"] == 2
    assert r["by_type"]["fix"] == 1
    assert r["entries"][0]["date"] == "2026-10-24"
