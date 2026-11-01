from app.services.app_marketplace_app_app_app_app_app_app_app_docs_gen import generate_endpoint_doc, build_docs_index

def test_endpoint():
    r = generate_endpoint_doc("GET", "/api/users", "List all users",
        [{"name": "page", "type": "integer", "required": False, "description": "Page number"}],
        {200: "Success", 401: "Unauthorized"})
    assert r["method"] == "GET"
    assert r["param_count"] == 1
    assert "200" in r["responses"]

def test_index():
    eps = [
        {"method": "GET", "path": "/users", "tag": "users"},
        {"method": "POST", "path": "/users", "tag": "users"},
        {"method": "GET", "path": "/health", "tag": "system"},
    ]
    r = build_docs_index(eps)
    assert r["total"] == 3
    assert r["tag_count"] == 2
    assert len(r["by_tag"]["users"]) == 2
