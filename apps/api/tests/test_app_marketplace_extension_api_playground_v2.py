from app.services.app_marketplace_extension_api_playground_v2 import ExtApiPlaygroundV2Service

def test_register_and_list():
    svc = ExtApiPlaygroundV2Service()
    svc.register_endpoint("ext-1", "/api/users", "GET", "List users")
    svc.register_endpoint("ext-1", "/api/users", "POST", "Create user")
    assert len(svc.get_endpoints("ext-1")) == 2

def test_generate_snippet():
    svc = ExtApiPlaygroundV2Service()
    ep = svc.register_endpoint("ext-1", "/api/data", "GET", "Get data")
    snippet = svc.generate_snippet(ep, "python")
    assert "requests.get" in snippet.code

def test_search():
    svc = ExtApiPlaygroundV2Service()
    svc.register_endpoint("ext-1", "/api/users", "GET", "List users")
    svc.register_endpoint("ext-1", "/api/data", "GET", "Get data")
    results = svc.search_endpoints("ext-1", "users")
    assert len(results) == 1
