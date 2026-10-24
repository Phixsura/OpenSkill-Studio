from app.services.app_version_timeline import build_version_timeline

def test_timeline():
    versions = [{"version": "2.0", "created_at": "2026-02", "review_status": "approved"},
                {"version": "1.0", "created_at": "2026-01", "review_status": "approved"}]
    tl = build_version_timeline(versions)
    assert tl[0]["is_latest"] is True
    assert tl[1]["is_first"] is True
    assert len(tl) == 2

def test_empty():
    assert build_version_timeline([]) == []
