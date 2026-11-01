from app.services.app_marketplace_extension_openapi_client import (
    OpenApiClientService,
)


SAMPLE_SPEC = {
    "openapi": "3.0.3",
    "info": {"title": "User Service", "version": "1.0.0"},
    "servers": [{"url": "https://api.example.com"}],
    "components": {
        "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}},
    },
    "paths": {
        "/api/users": {
            "get": {"summary": "List users", "operationId": "list_users",
                    "parameters": [{"name": "page", "in": "query", "schema": {"type": "integer"}}]},
            "post": {"summary": "Create user", "operationId": "create_user",
                     "requestBody": {"content": {"application/json": {}}}},
        },
        "/api/users/{id}": {
            "get": {"summary": "Get user", "operationId": "get_user",
                    "parameters": [{"name": "id", "in": "path", "schema": {"type": "string"}}]},
            "delete": {"summary": "Delete user", "operationId": "delete_user"},
        },
    },
}


def test_parse_spec():
    svc = OpenApiClientService()
    client = svc.parse_spec(SAMPLE_SPEC)
    assert client.class_name == "UserServiceClient"
    assert client.base_url == "https://api.example.com"
    assert client.auth_type == "bearer"
    assert len(client.methods) == 4


def test_method_names():
    svc = OpenApiClientService()
    client = svc.parse_spec(SAMPLE_SPEC)
    names = {m.name for m in client.methods}
    assert "listUsers" in names
    assert "createUser" in names
    assert "getUser" in names


def test_has_body():
    svc = OpenApiClientService()
    client = svc.parse_spec(SAMPLE_SPEC)
    create = next(m for m in client.methods if m.name == "createUser")
    assert create.has_body is True
    get = next(m for m in client.methods if m.name == "listUsers")
    assert get.has_body is False


def test_generate_typescript():
    svc = OpenApiClientService()
    client = svc.parse_spec(SAMPLE_SPEC)
    ts = svc.generate_typescript(client)
    assert "class UserServiceClient" in ts
    assert "async listUsers" in ts
    assert "page: number" in ts
    assert "body: Record" in ts


def test_generate_python():
    svc = OpenApiClientService()
    client = svc.parse_spec(SAMPLE_SPEC)
    py = svc.generate_python(client)
    assert "class UserServiceClient:" in py
    assert "def listUsers" in py
    assert "httpx" in py


def test_empty_spec():
    svc = OpenApiClientService()
    client = svc.parse_spec({"openapi": "3.0.3", "info": {"title": "Empty"}, "paths": {}})
    assert client.class_name == "EmptyClient"
    assert len(client.methods) == 0


def test_no_operation_id():
    svc = OpenApiClientService()
    spec = {"openapi": "3.0.3", "info": {"title": "Api"},
            "paths": {"/items": {"get": {"summary": "Get items"}}}}
    client = svc.parse_spec(spec)
    assert client.methods[0].name == "getItems"
