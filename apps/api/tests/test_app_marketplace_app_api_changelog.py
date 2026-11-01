from app.services.app_marketplace_app_api_changelog import build_api_changelog

def test_changelog():
    changes = [
        {"type": "added", "endpoint": "GET /api/v2/users", "description": "New users endpoint"},
        {"type": "removed", "endpoint": "GET /api/v1/users", "description": "Deprecated v1 endpoint"},
        {"type": "fixed", "endpoint": "POST /api/apps", "description": "Fix validation"},
    ]
    r = build_api_changelog(version="v2", changes=changes)
    assert r["total_changes"] == 3
    assert r["has_breaking"]
    assert len(r["breaking_changes"]) == 1

def test_no_breaking():
    r = build_api_changelog(version="v1.1", changes=[{"type": "fixed", "description": "Bug fix"}])
    assert not r["has_breaking"]
