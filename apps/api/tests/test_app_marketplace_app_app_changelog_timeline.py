from app.services.app_marketplace_app_app_changelog_timeline import build_changelog_timeline

def test_timeline():
    versions = [
        {"version": "2.0.0", "date": "2026-10-01", "title": "Major Redesign",
         "changes": [{"type": "feature", "breaking": True}, {"type": "feature"}, {"type": "fix"}]},
        {"version": "1.1.0", "date": "2026-09-01",
         "changes": [{"type": "feature"}, {"type": "fix"}]},
    ]
    r = build_changelog_timeline(versions=versions)
    assert r["total_versions"] == 2
    assert r["total_changes"] == 5
    assert r["timeline"][0]["features"] == 2
    assert r["timeline"][0]["breaking"] == 1

def test_empty():
    r = build_changelog_timeline(versions=[])
    assert r["total_versions"] == 0
