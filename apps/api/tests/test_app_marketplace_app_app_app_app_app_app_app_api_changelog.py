from app.services.app_marketplace_app_app_app_app_app_app_app_api_changelog import generate_changelog

def test_changelog():
    entries = [
        {"type": "breaking", "endpoint": "/api/v1/users", "description": "Removed email field", "version": "3.0"},
        {"type": "added", "endpoint": "/api/v1/exports", "description": "New export endpoint", "version": "3.0"},
        {"type": "fixed", "endpoint": "/api/v1/auth", "description": "Token refresh bug", "version": "3.0"},
    ]
    r = generate_changelog(entries)
    assert r["total_changes"] == 3
    assert r["has_breaking"]
    assert r["severity"] == "major"
    assert len(r["sections"]) == 3
    assert r["sections"][0]["type"] == "breaking"

def test_no_breaking():
    entries = [{"type": "added", "endpoint": "/new", "description": "New"}]
    r = generate_changelog(entries)
    assert not r["has_breaking"]
    assert r["severity"] == "minor"
