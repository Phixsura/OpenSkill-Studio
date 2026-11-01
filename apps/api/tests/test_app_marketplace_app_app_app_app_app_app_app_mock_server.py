from app.services.app_marketplace_app_app_app_app_app_app_app_mock_server import MockServer

def test_mock():
    ms = MockServer()
    ms.register("GET", "/api/users", 200, {"users": []})
    r = ms.handle("GET", "/api/users")
    assert r["mocked"]
    assert r["status"] == 200
    assert r["body"]["users"] == []
    assert r["call_number"] == 1

def test_not_found():
    ms = MockServer()
    r = ms.handle("GET", "/missing")
    assert not r["mocked"]
    assert r["status"] == 404

def test_stats():
    ms = MockServer()
    ms.register("GET", "/a", 200)
    ms.handle("GET", "/a")
    ms.handle("GET", "/a")
    assert ms.stats()["total_calls"] == 2
