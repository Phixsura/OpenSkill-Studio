from app.services.app_marketplace_app_openapi_generator import generate_openapi_spec, validate_openapi_spec, render_openapi_yaml_header

def test_generate():
    spec = generate_openapi_spec(
        app={"name": "MyApp", "slug": "my-app", "version": "2.0.0", "description": "Great app"},
        endpoints=[{"path": "/users", "method": "GET", "summary": "List users", "tags": ["users"]},
                   {"path": "/users", "method": "POST", "summary": "Create user"}])
    assert spec["openapi"] == "3.0.3"
    assert spec["info"]["title"] == "MyApp API"
    assert "/users" in spec["paths"]
    assert "get" in spec["paths"]["/users"]
    assert "post" in spec["paths"]["/users"]

def test_validate_ok():
    spec = {"openapi": "3.0.3", "info": {"title": "X", "version": "1.0"}, "paths": {"/a": {}}}
    r = validate_openapi_spec(spec=spec)
    assert r["valid"]

def test_validate_missing():
    r = validate_openapi_spec(spec={})
    assert not r["valid"]
    assert len(r["errors"]) >= 2

def test_yaml():
    spec = {"openapi": "3.0.3", "info": {"title": "MyApp API", "version": "1.0", "description": "D"}, "paths": {"/a": {}, "/b": {}}}
    y = render_openapi_yaml_header(spec=spec)
    assert "MyApp API" in y
    assert "2 endpoints" in y
