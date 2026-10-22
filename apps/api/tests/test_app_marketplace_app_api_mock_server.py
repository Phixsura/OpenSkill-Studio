from app.services.app_marketplace_app_api_mock_server import create_mock_endpoint, match_request, generate_mock_data, build_mock_server_config

def test_create():
    m = create_mock_endpoint(path="/users", method="GET", response_body={"users": []})
    assert m["status_code"] == 200
    assert m["response_body"]["users"] == []

def test_match():
    mocks = [create_mock_endpoint(path="/users", method="GET"),
             create_mock_endpoint(path="/users", method="POST", status_code=201)]
    r = match_request(mocks=mocks, method="POST", path="/users")
    assert r["status_code"] == 201

def test_no_match():
    assert match_request(mocks=[], method="GET", path="/x") is None

def test_generate():
    schema = {"properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "active": {"type": "boolean"}}}
    d = generate_mock_data(schema=schema)
    assert d["name"] == "mock_name"
    assert d["age"] == 42

def test_config():
    eps = [create_mock_endpoint(path="/a", method="GET")]
    c = build_mock_server_config(endpoints=eps)
    assert c["endpoint_count"] == 1
    assert c["cors_enabled"]
