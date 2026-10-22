from app.services.app_developer_changelog_builder import build_developer_changelog

def test_build():
    apps = [
        {"name": "A", "slug": "a", "versions": [{"version": "2.0", "created_at": "2026-02"}, {"version": "1.0", "created_at": "2026-01"}]},
        {"name": "B", "slug": "b", "versions": [{"version": "1.0", "created_at": "2026-03"}]},
    ]
    cl = build_developer_changelog(apps)
    assert len(cl) == 3
    assert cl[0]["created_at"] == "2026-03"

def test_empty():
    assert build_developer_changelog([]) == []
