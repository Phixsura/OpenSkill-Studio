from app.services.app_marketplace_app_app_app_app_app_app_app_openapi_gen import generate_spec, spec_stats

def test_generate():
    r = generate_spec("My API", "1.0.0", [
        {"method": "GET", "path": "/users", "tag": "users", "summary": "List users"},
        {"method": "POST", "path": "/users", "tag": "users", "summary": "Create user"},
        {"method": "GET", "path": "/health", "tag": "system", "summary": "Health check"},
    ])
    assert r["openapi"] == "3.0.3"
    assert r["endpoint_count"] == 3
    assert r["path_count"] == 2
    assert "users" in r["tags"]

def test_stats():
    spec = generate_spec("API", "1.0", [
        {"method": "GET", "path": "/a"}, {"method": "POST", "path": "/b"},
        {"method": "GET", "path": "/c"},
    ])
    s = spec_stats(spec)
    assert s["endpoints"] == 3
    assert s["by_method"]["get"] == 2
