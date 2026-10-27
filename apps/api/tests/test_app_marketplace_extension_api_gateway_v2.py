from app.services.app_marketplace_extension_api_gateway_v2 import ApiGatewayV2Service, GatewayRequest

def test_successful_request():
    gw = ApiGatewayV2Service()
    gw.register_route("/api/users", "user-service", require_auth=False)
    resp = gw.handle(GatewayRequest("GET", "/api/users"))
    assert resp.status_code == 200
    assert resp.body["upstream"] == "user-service"

def test_auth_required():
    gw = ApiGatewayV2Service()
    gw.register_route("/api/data", "data-service")
    resp = gw.handle(GatewayRequest("GET", "/api/data"))
    assert resp.status_code == 401

def test_auth_success():
    gw = ApiGatewayV2Service()
    gw.register_route("/api/data", "data-service")
    gw.register_token("valid-token")
    resp = gw.handle(GatewayRequest("GET", "/api/data",
                     headers={"Authorization": "Bearer valid-token"}))
    assert resp.status_code == 200

def test_route_not_found():
    gw = ApiGatewayV2Service()
    resp = gw.handle(GatewayRequest("GET", "/unknown"))
    assert resp.status_code == 404

def test_rate_limit():
    gw = ApiGatewayV2Service()
    gw.register_route("/api/fast", "svc", require_auth=False, rate_limit=3)
    for _ in range(3):
        gw.handle(GatewayRequest("GET", "/api/fast", client_id="c1"))
    resp = gw.handle(GatewayRequest("GET", "/api/fast", client_id="c1"))
    assert resp.status_code == 429

def test_metrics():
    gw = ApiGatewayV2Service()
    gw.register_route("/api/x", "svc", require_auth=False)
    gw.handle(GatewayRequest("GET", "/api/x"))
    gw.handle(GatewayRequest("GET", "/nowhere"))  # 404
    m = gw.get_metrics()
    assert m["total_requests"] == 1  # only successful logged
    assert m["error_count"] == 0
