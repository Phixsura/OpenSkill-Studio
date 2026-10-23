from app.services.app_marketplace_app_marketplace_app_version_history import build_version_history, get_version_diff_summary

def test_history():
    versions = [{"version": "2.0", "released_at": "2026-06-01", "changes": [{"x": 1}]},
                {"version": "1.0", "released_at": "2026-01-01", "changes": []}]
    r = build_version_history(versions=versions)
    assert r["total"] == 2
    assert r["versions"][0]["is_latest"]
    assert r["latest_version"] == "2.0"

def test_diff_summary():
    r = get_version_diff_summary(from_version={"version": "1.0", "changes": [1, 2]},
                                   to_version={"version": "2.0", "changes": [1, 2, 3, 4, 5]})
    assert r["net_changes"] == 3
