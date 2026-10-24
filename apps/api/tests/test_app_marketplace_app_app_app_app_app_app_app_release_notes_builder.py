from app.services.app_marketplace_app_app_app_app_app_app_app_release_notes_builder import compile_release_notes

def test_notes():
    r = compile_release_notes(version="3.5.0", date="2026-10-24", prs=[
        {"title": "Add SSO", "number": 100, "type": "added", "author": "alice"},
        {"title": "Fix login", "number": 101, "type": "fixed", "author": "bob"},
        {"title": "Add dark mode", "number": 102, "type": "added", "author": "alice"},
    ])
    assert r["total_prs"] == 3
    assert r["contributor_count"] == 2
    assert not r["has_breaking"]
    assert r["sections"][0]["type"] == "added"
    assert r["sections"][0]["count"] == 2
