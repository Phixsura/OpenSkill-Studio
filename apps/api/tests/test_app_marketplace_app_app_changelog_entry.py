from app.services.app_marketplace_app_app_changelog_entry import create_changelog_entry

def test_entry():
    changes = [
        {"type": "feature", "description": "Dark mode"},
        {"type": "fix", "description": "Login crash"},
        {"type": "feature", "description": "Export CSV"},
    ]
    r = create_changelog_entry(version="2.1.0", date="2026-10-23", changes=changes)
    assert r["version"] == "2.1.0"
    assert r["total_changes"] == 3
    assert not r["has_breaking"]
    assert len(r["categories"]) == 2

def test_breaking():
    r = create_changelog_entry(version="3.0", changes=[{"type": "breaking", "description": "Removed v1", "breaking": True}])
    assert r["has_breaking"]

def test_xss():
    r = create_changelog_entry(version="1.0", changes=[{"description": "<script>alert(1)</script>"}])
    assert "<script>" not in r["categories"][0]["items"][0]
