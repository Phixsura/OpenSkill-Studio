from app.services.app_marketplace_app_api_versioning import create_api_version, route_to_version, build_version_matrix

def test_create():
    r = create_api_version(app_id="a1", version="v2", endpoints=[{"path": "/users", "method": "GET"}])
    assert r["endpoint_count"] == 1

def test_invalid_version():
    r = create_api_version(app_id="a1", version="2", endpoints=[])
    assert r["error"]

def test_route_found():
    r = route_to_version(requested_version="v2", available=["v1", "v2"])
    assert r["version"] == "v2"
    assert not r["fallback"]

def test_route_fallback():
    r = route_to_version(requested_version="v3", available=["v1", "v2"])
    assert r["fallback"]

def test_matrix():
    versions = [
        {"version": "v1", "endpoints": [{"path": "/users"}, {"path": "/apps"}]},
        {"version": "v2", "endpoints": [{"path": "/users"}, {"path": "/orgs"}]},
    ]
    m = build_version_matrix(versions=versions)
    assert len(m["matrix"]) == 3  # /apps, /orgs, /users
