from app.services.app_marketplace_app_openapi_spec import generate_openapi_spec

def test_generate():
    endpoints = [
        {"path": "/apps", "method": "GET", "description": "List apps"},
        {"path": "/apps", "method": "POST", "description": "Create app",
         "request_body": {"type": "object", "properties": {"name": {"type": "string"}}}},
        {"path": "/apps/{id}", "method": "GET", "description": "Get app"},
    ]
    r = generate_openapi_spec(app_name="MyApp", version="1.0.0",
        base_url="https://api.example.com", endpoints=endpoints)
    assert r["spec"]["openapi"] == "3.0.3"
    assert r["endpoint_count"] == 3
    assert r["path_count"] == 2  # /apps and /apps/{id}
    assert "/apps" in r["spec"]["paths"]

def test_empty():
    r = generate_openapi_spec(app_name="X", version="1.0", base_url="https://x.com", endpoints=[])
    assert r["endpoint_count"] == 0
