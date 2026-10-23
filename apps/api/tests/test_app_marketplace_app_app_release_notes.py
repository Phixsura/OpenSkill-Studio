from app.services.app_marketplace_app_app_release_notes import build_release_notes

def test_release():
    items = [
        {"category": "feature", "title": "Dark mode", "author": "Alice", "pr": 42},
        {"category": "fix", "title": "Login crash", "author": "Bob"},
        {"category": "breaking", "title": "Removed v1 API"},
    ]
    r = build_release_notes(version="2.0.0", date="2026-03-01", items=items)
    assert r["version"] == "2.0.0"
    assert r["total_items"] == 3
    assert r["has_breaking"]
    assert not r["has_security"]
    assert len(r["categories"]["feature"]) == 1

def test_empty():
    r = build_release_notes(version="1.0.0", items=[])
    assert r["total_items"] == 0
