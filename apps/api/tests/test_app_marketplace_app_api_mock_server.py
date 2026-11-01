from app.services.app_marketplace_app_api_mock_server import create_mock_endpoint, create_mock_collection

def test_create():
    r = create_mock_endpoint(path="/api/users", method="GET", status_code=200,
        response_body={"users": []})
    assert r["mock_id"].startswith("mock_")
    assert r["method"] == "GET"
    assert r["url"].endswith("/api/users")

def test_with_delay():
    r = create_mock_endpoint(path="/slow", delay_ms=2000)
    assert r["delay_ms"] == 2000

def test_too_slow():
    r = create_mock_endpoint(path="/x", delay_ms=20000)
    assert "error" in r

def test_collection():
    eps = [{"path": "/users", "method": "GET"}, {"path": "/users", "method": "POST"}]
    r = create_mock_collection(name="User API", endpoints=eps)
    assert r["total_created"] == 2
    assert r["collection_name"] == "User API"
