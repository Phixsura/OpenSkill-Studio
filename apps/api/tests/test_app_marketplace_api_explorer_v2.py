from app.services.app_marketplace_api_explorer_v2 import build_endpoint_card, validate_response_schema, generate_sample_request

def test_card():
    c = build_endpoint_card(method="GET", path="/users", summary="List users",
                              parameters=[{"name": "limit", "type": "integer"}], auth_required=True)
    assert c["method"] == "GET"
    assert "Bearer" in c["curl_example"]

def test_validate_ok():
    schema = {"properties": {"id": {"type": "string", "required": True}}}
    r = validate_response_schema(response={"id": "abc"}, expected_schema=schema)
    assert r["valid"]

def test_validate_missing():
    schema = {"properties": {"id": {"type": "string", "required": True}}}
    r = validate_response_schema(response={}, expected_schema=schema)
    assert not r["valid"]

def test_sample():
    ep = {"method": "POST", "path": "/apps", "parameters": [{"name": "name", "type": "string"}]}
    r = generate_sample_request(endpoint=ep)
    assert r["params"]["name"] == "example_name"
