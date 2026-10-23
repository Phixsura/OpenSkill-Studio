from app.services.app_marketplace_app_developer_api_explorer import build_api_explorer, generate_example_request, generate_example_response

def test_explorer():
    endpoints = [{"method": "GET", "path": "/users", "tag": "users", "summary": "List users"},
                 {"method": "POST", "path": "/apps", "tag": "apps", "summary": "Create app"}]
    e = build_api_explorer(endpoints=endpoints, base_url="https://api.openskill.dev")
    assert e["total_endpoints"] == 2
    assert "users" in e["groups"]

def test_example_request():
    ep = {"method": "GET", "try_url": "https://api.com/users", "parameters": [{"name": "limit", "type": "integer"}]}
    r = generate_example_request(endpoint=ep)
    assert r["params"]["limit"] == 1

def test_example_response():
    r = generate_example_response(schema={"properties": {"id": {"type": "string"}, "count": {"type": "integer"}}})
    assert r["body"]["id"] == "example_id"
    assert r["body"]["count"] == 0
