from app.services.app_marketplace_extension_api_doc_generator import (
    ApiDocGeneratorService,
)
import json


def test_generate_basic_spec():
    svc = ApiDocGeneratorService()
    svc.set_info("My API", "2.0.0", "Extension API docs")
    svc.add_endpoint("GET", "/api/v1/items", "List items", tags=["items"])
    spec = svc.generate()
    assert spec["openapi"] == "3.0.3"
    assert spec["info"]["title"] == "My API"
    assert "/api/v1/items" in spec["paths"]
    assert "get" in spec["paths"]["/api/v1/items"]


def test_endpoint_with_params():
    svc = ApiDocGeneratorService()
    svc.add_endpoint("GET", "/api/v1/items/{id}", "Get item",
                     params=[{"name": "id", "in": "path", "type": "string", "description": "Item ID"}])
    spec = svc.generate()
    params = spec["paths"]["/api/v1/items/{id}"]["get"]["parameters"]
    assert len(params) == 1
    assert params[0]["name"] == "id"
    assert params[0]["in"] == "path"


def test_request_body():
    svc = ApiDocGeneratorService()
    svc.add_endpoint("POST", "/api/v1/items", "Create item",
                     request_body={"type": "object", "properties": {"name": {"type": "string"}}})
    spec = svc.generate()
    assert "requestBody" in spec["paths"]["/api/v1/items"]["post"]


def test_auth_security():
    svc = ApiDocGeneratorService()
    svc.add_endpoint("GET", "/api/v1/protected", "Protected", auth_required=True)
    svc.add_endpoint("GET", "/api/v1/public", "Public", auth_required=False)
    spec = svc.generate()
    assert "security" in spec["paths"]["/api/v1/protected"]["get"]
    assert "security" not in spec["paths"]["/api/v1/public"]["get"]


def test_deprecated():
    svc = ApiDocGeneratorService()
    svc.add_endpoint("GET", "/api/v1/old", "Old endpoint", deprecated=True)
    spec = svc.generate()
    assert spec["paths"]["/api/v1/old"]["get"]["deprecated"] is True


def test_generate_json():
    svc = ApiDocGeneratorService()
    svc.add_endpoint("GET", "/health", "Health check", auth_required=False)
    text = svc.generate_json()
    parsed = json.loads(text)
    assert parsed["openapi"] == "3.0.3"


def test_tags():
    svc = ApiDocGeneratorService()
    svc.add_endpoint("GET", "/a", "A", tags=["users"])
    svc.add_endpoint("GET", "/b", "B", tags=["items", "users"])
    assert svc.get_tags() == ["items", "users"]


def test_servers():
    svc = ApiDocGeneratorService()
    svc.add_server("https://api.example.com", "Production")
    svc.add_endpoint("GET", "/test", "Test")
    spec = svc.generate()
    assert spec["servers"][0]["url"] == "https://api.example.com"
