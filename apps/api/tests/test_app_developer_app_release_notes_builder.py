from app.services.app_developer_app_release_notes_builder import build_release_notes

def test_with_changelog():
    r = build_release_notes(version="2.0", changelog="Big update", diff_summary=None, breaking=False, new_permissions=[])
    assert any(s["content"] == "Big update" for s in r["sections"])

def test_breaking():
    r = build_release_notes(version="3.0", changelog=None, diff_summary=None, breaking=True, new_permissions=["write:cohorts"])
    assert r["breaking"] is True
    assert any("breaking" in s["type"] for s in r["sections"])

def test_default():
    r = build_release_notes(version="1.1", changelog=None, diff_summary=None, breaking=False, new_permissions=[])
    assert any("Minor" in s["content"] for s in r["sections"])
