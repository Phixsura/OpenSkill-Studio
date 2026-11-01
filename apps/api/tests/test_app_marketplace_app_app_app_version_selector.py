from app.services.app_marketplace_app_app_app_version_selector import build_version_selector

def test_selector():
    versions = [
        {"version": "1.0.0", "published_at": "2026-01-01", "downloads": 5000},
        {"version": "2.0.0", "published_at": "2026-03-01", "downloads": 2000},
        {"version": "2.1.0-beta.1", "published_at": "2026-04-01", "downloads": 100},
    ]
    r = build_version_selector(versions=versions, current="2.0.0")
    assert r["total"] == 3
    assert r["latest_stable"] == "2.0.0"
    assert r["versions"][0]["is_prerelease"]  # newest first

def test_compatibility():
    versions = [{"version": "1.0.0", "published_at": "2026-01-01"},
                {"version": "2.0.0", "published_at": "2026-03-01"}]
    r = build_version_selector(versions=versions, min_compatible="2.0.0")
    assert not r["versions"][1]["compatible"]  # 1.0.0 < 2.0.0
    assert r["versions"][0]["compatible"]       # 2.0.0 >= 2.0.0
