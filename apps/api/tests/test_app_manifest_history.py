from app.services.app_manifest_history import build_history_entry, build_full_history

def test_initial():
    e = build_history_entry(version="1.0.0", manifest={"app": {"name": "X"}})
    assert e["is_initial"] is True
    assert e["change_count"] == 0

def test_with_changes():
    e = build_history_entry(version="2.0", manifest={"a": 2}, previous_manifest={"a": 1})
    assert e["change_count"] > 0
    assert e["is_initial"] is False

def test_full_history():
    versions = [
        {"version": "1.0", "manifest": {"name": "X"}},
        {"version": "2.0", "manifest": {"name": "Y"}},
        {"version": "3.0", "manifest": {"name": "Y", "new": True}},
    ]
    h = build_full_history(versions)
    assert len(h) == 3
    assert h[0]["is_initial"] is True
    assert h[1]["change_count"] > 0
