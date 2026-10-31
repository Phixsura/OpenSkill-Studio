from app.services.app_marketplace_extension_api_mock_server import (
    ApiMockServerService,
)


def test_simple_mock():
    svc = ApiMockServerService()
    svc.add_endpoint("GET", "/api/users", 200, {"users": []})
    resp = svc.handle_request("GET", "/api/users")
    assert resp["status_code"] == 200
    assert "users" in resp["body"]


def test_path_param():
    svc = ApiMockServerService()
    svc.add_endpoint("GET", "/api/users/{id}", 200, {"id": "matched"})
    resp = svc.handle_request("GET", "/api/users/123")
    assert resp["status_code"] == 200


def test_no_match_404():
    svc = ApiMockServerService()
    resp = svc.handle_request("GET", "/unknown")
    assert resp["status_code"] == 404


def test_header_matching():
    svc = ApiMockServerService()
    svc.add_endpoint("POST", "/api/data", 201, {"created": True},
                     match_headers={"Authorization": "Bearer test"})
    resp = svc.handle_request("POST", "/api/data", {"Authorization": "Bearer test"})
    assert resp["status_code"] == 201
    resp2 = svc.handle_request("POST", "/api/data", {})
    assert resp2["status_code"] == 404


def test_body_matching():
    svc = ApiMockServerService()
    svc.add_endpoint("POST", "/api/action", 200, {"ok": True},
                     match_body={"action": "deploy"})
    resp = svc.handle_request("POST", "/api/action", body='{"action": "deploy"}')
    assert resp["status_code"] == 200
    resp2 = svc.handle_request("POST", "/api/action", body='{"action": "rollback"}')
    assert resp2["status_code"] == 404


def test_request_recording():
    svc = ApiMockServerService()
    ep = svc.add_endpoint("GET", "/api/health", 200, {"ok": True})
    svc.handle_request("GET", "/api/health")
    svc.handle_request("GET", "/api/health")
    reqs = svc.get_requests(ep.endpoint_id)
    assert len(reqs) == 2
    assert ep.call_count == 2


def test_reset():
    svc = ApiMockServerService()
    svc.add_endpoint("GET", "/test", 200)
    svc.handle_request("GET", "/test")
    count = svc.reset()
    assert count == 1
    assert len(svc.get_requests()) == 0


def test_custom_status_and_latency():
    svc = ApiMockServerService()
    svc.add_endpoint("DELETE", "/api/item", 204, "", latency_ms=500)
    resp = svc.handle_request("DELETE", "/api/item")
    assert resp["status_code"] == 204
    assert resp["latency_ms"] == 500
