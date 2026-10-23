from app.services.app_marketplace_app_app_app_app_app_app_app_api_mock_server import MockServer

def test_mock():
    srv = MockServer()
    srv.add_mock(method="GET", path="/api/users", body={"users": []})
    srv.add_mock(method="GET", path="/api/users/:id", status=200, body={"id": "1", "name": "Alice"})
    srv.add_mock(method="POST", path="/api/users", status=201, body={"created": True})
    r = srv.match("GET", "/api/users")
    assert r["matched"]
    assert r["body"]["users"] == []
    r2 = srv.match("GET", "/api/users/123")
    assert r2["matched"]
    assert r2["body"]["name"] == "Alice"
    r3 = srv.match("DELETE", "/api/users")
    assert not r3["matched"]
    s = srv.stats()
    assert s["total_hits"] == 2
    assert s["total_mocks"] == 3
