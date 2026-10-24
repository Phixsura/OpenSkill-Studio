from app.services.app_marketplace_app_app_app_app_app_app_app_release_cal import create_release, release_timeline

def test_release():
    r = create_release("4.0", "2025-01-15", ["Dark mode", "API v4", "RBAC"], "alice")
    assert r["feature_count"] == 3

def test_timeline():
    releases = [
        create_release("3.0", "2024-10-01", ["A", "B"], status="released"),
        create_release("3.1", "2024-11-15", ["C"], status="in_progress"),
        create_release("4.0", "2025-01-15", ["D", "E", "F"], status="planned"),
    ]
    r = release_timeline(releases)
    assert r["released"] == 1
    assert r["planned"] == 1
    assert r["total_features"] == 6
