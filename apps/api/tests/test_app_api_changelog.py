from app.services.app_api_changelog import get_api_changelog, get_latest_api_version, get_changes_since

def test_changelog():
    cl = get_api_changelog()
    assert len(cl) >= 1
    assert "changes" in cl[0]

def test_latest():
    v = get_latest_api_version()
    assert v == "2024-01-01"

def test_changes_since():
    changes = get_changes_since("2023-01-01")
    assert len(changes) >= 6

def test_no_changes():
    changes = get_changes_since("2099-01-01")
    assert len(changes) == 0
