from app.services.app_marketplace_app_app_app_app_app_app_app_api_versioning import (
    create_version, build_version_matrix, check_deprecation,
)

def test_matrix():
    versions = [
        create_version("v1", "sunset"),
        create_version("v2", "deprecated"),
        create_version("v3", "active"),
    ]
    m = build_version_matrix(versions)
    assert m["active_count"] == 1
    assert m["deprecated_count"] == 1
    assert m["latest"] == "v3"

def test_deprecation():
    v = create_version("v2", "deprecated")
    r = check_deprecation(v)
    assert r["action_needed"]
    assert "deprecated" in r["message"]
    v2 = create_version("v3", "active")
    r2 = check_deprecation(v2)
    assert not r2["action_needed"]
