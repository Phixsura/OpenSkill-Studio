from app.services.app_marketplace_app_app_app_app_app_app_app_api_playground import (
    build_request, simulate_response, save_to_history,
)

def test_request_response():
    req = build_request("POST", "/api/users", body='{"name":"Alice"}')
    assert req["method"] == "POST"
    resp = simulate_response(req)
    assert resp["status"] == 201
    assert resp["response_ms"] > 0

def test_history():
    req = build_request("GET", "/api/health")
    resp = simulate_response(req)
    h = save_to_history(req, resp)
    assert h["method"] == "GET"
    assert h["status"] == 200
