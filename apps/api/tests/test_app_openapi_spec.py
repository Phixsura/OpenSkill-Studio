from app.services.app_openapi_spec import generate_app_openapi

def test_basic():
    spec = generate_app_openapi(app_name="My App", app_slug="my-app", version="1.0.0", permissions=["read:cohorts"])
    assert spec["openapi"] == "3.0.3"
    assert spec["info"]["title"] == "My App API"

def test_has_permissions():
    spec = generate_app_openapi(app_name="X", app_slug="x", version="1.0", permissions=["read:cohorts", "write:projects"])
    assert len(spec["x-permissions"]) == 2

def test_with_endpoints():
    eps = [{"path": "/cohorts", "method": "GET", "summary": "List cohorts"}]
    spec = generate_app_openapi(app_name="X", app_slug="x", version="1.0", permissions=[], endpoints=eps)
    assert "/cohorts" in spec["paths"]

def test_security_scheme():
    spec = generate_app_openapi(app_name="X", app_slug="x", version="1.0", permissions=[])
    assert "apiKey" in spec["components"]["securitySchemes"]

def test_server_url():
    spec = generate_app_openapi(app_name="X", app_slug="my-app", version="1.0", permissions=[])
    assert "my-app" in spec["servers"][0]["url"]
