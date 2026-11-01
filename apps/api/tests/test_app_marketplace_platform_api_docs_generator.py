from app.services.app_marketplace_platform_api_docs_generator import generate_api_docs, generate_curl_examples, build_api_reference_page

def test_docs():
    routes = [{"method": "GET", "path": "/apps", "tag": "apps", "summary": "List apps"},
              {"method": "POST", "path": "/apps", "tag": "apps", "summary": "Create app"},
              {"method": "GET", "path": "/users", "tag": "users", "summary": "List users"}]
    d = generate_api_docs(routes=routes)
    assert d["total_endpoints"] == 3
    assert d["group_count"] == 2
    assert "apps" in d["groups"]

def test_curl():
    routes = [{"method": "GET", "path": "/apps", "auth_required": True},
              {"method": "POST", "path": "/apps", "auth_required": True}]
    c = generate_curl_examples(routes=routes)
    assert "Bearer" in c[0]["curl"]
    assert "Content-Type" in c[1]["curl"]

def test_reference_page():
    docs = {"title": "API", "version": "v2", "total_endpoints": 50, "groups": {"apps": [], "users": []}}
    p = build_api_reference_page(docs=docs, examples=[{"method": "GET", "path": "/apps", "curl": "curl ..."}])
    assert p["page_type"] == "api_reference"
    assert p["endpoint_count"] == 50
    assert p["try_it_enabled"]
