from app.services.app_marketplace_app_api_versioning import create_api_version, deprecate_version, get_version_matrix

def test_create():
    r = create_api_version(app_id="a1", version="v2", changelog="New endpoints")
    assert r["status"] == "active"
    assert r["version"] == "v2"

def test_invalid():
    r = create_api_version(app_id="a1", version="2.0", changelog="x")
    assert "error" in r

def test_deprecate():
    r = deprecate_version(version="v1", sunset_days=60)
    assert r["status"] == "deprecated"
    assert r["sunset_days_remaining"] == 60

def test_matrix():
    versions = [{"version": "v3", "status": "active"}, {"version": "v2", "status": "deprecated"},
                {"version": "v1", "status": "sunset"}]
    r = get_version_matrix(versions=versions)
    assert r["active_count"] == 1
    assert r["latest"] == "v3"
