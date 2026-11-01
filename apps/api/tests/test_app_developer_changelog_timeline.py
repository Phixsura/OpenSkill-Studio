from app.services.app_developer_changelog_timeline import build_changelog_timeline

def test_timeline():
    cls = [
        {"app_name": "A", "entries": [{"version": "2.0", "date": "2026-03"}]},
        {"app_name": "B", "entries": [{"version": "1.0", "date": "2026-04"}]},
    ]
    tl = build_changelog_timeline(cls)
    assert tl[0]["app_name"] == "B"
    assert len(tl) == 2

def test_limit():
    cls = [{"app_name": "A", "entries": [{"version": f"{i}.0", "date": f"2026-{i:02d}"} for i in range(1, 13)]}]
    assert len(build_changelog_timeline(cls, limit=5)) == 5
