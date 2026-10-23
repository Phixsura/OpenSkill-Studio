from app.services.app_marketplace_app_app_openapi_validator import validate_openapi

def test_valid():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "My API", "version": "1.0.0"},
        "paths": {"/apps": {"get": {"summary": "List apps", "operationId": "listApps"}}},
    }
    r = validate_openapi(spec=spec)
    assert r["valid"]
    assert r["endpoint_count"] == 1
    assert r["title"] == "My API"

def test_missing_fields():
    r = validate_openapi(spec={})
    assert not r["valid"]
    assert len(r["errors"]) >= 3

def test_warnings():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "API", "version": "1.0"},
        "paths": {"/test": {"get": {}}},
    }
    r = validate_openapi(spec=spec)
    assert r["valid"]
    assert len(r["warnings"]) == 1
