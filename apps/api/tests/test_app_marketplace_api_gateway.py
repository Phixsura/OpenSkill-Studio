from app.services.app_marketplace_api_gateway import (
    APIGateway, GatewayRoute, GatewayRequest,
)


def _setup_gateway() -> APIGateway:
    gw = APIGateway()
    gw.register_route(GatewayRoute("/api/ext/slack", "slack-ext", ["GET", "POST"]))
    gw.register_route(GatewayRoute("/api/ext/public", "pub-ext", ["GET"], requires_auth=False))
    gw.register_api_key("valid-key-123", "slack-ext")
    return gw


def test_successful_request():
    gw = _setup_gateway()
    resp = gw.handle_request(GatewayRequest("GET", "/api/ext/slack/channels", api_key="valid-key-123"))
    assert resp.status_code == 200
    assert resp.body["processed"] is True


def test_route_not_found():
    gw = _setup_gateway()
    resp = gw.handle_request(GatewayRequest("GET", "/api/unknown"))
    assert resp.status_code == 404


def test_auth_required():
    gw = _setup_gateway()
    resp = gw.handle_request(GatewayRequest("GET", "/api/ext/slack/data"))
    assert resp.status_code == 401
    assert "API key required" in resp.body["error"]


def test_invalid_key():
    gw = _setup_gateway()
    resp = gw.handle_request(GatewayRequest("GET", "/api/ext/slack/data", api_key="bad-key"))
    assert resp.status_code == 401


def test_public_route_no_auth():
    gw = _setup_gateway()
    resp = gw.handle_request(GatewayRequest("GET", "/api/ext/public/info"))
    assert resp.status_code == 200


def test_rate_limit():
    gw = APIGateway()
    gw.register_route(GatewayRoute("/api/limited", "lim-ext", ["GET"], rate_limit=3))
    gw.register_api_key("key", "lim-ext")
    for _ in range(3):
        assert gw.handle_request(GatewayRequest("GET", "/api/limited", api_key="key")).status_code == 200
    assert gw.handle_request(GatewayRequest("GET", "/api/limited", api_key="key")).status_code == 429


def test_request_log():
    gw = _setup_gateway()
    gw.handle_request(GatewayRequest("GET", "/api/ext/slack/test", api_key="valid-key-123"))
    log = gw.get_request_log("slack-ext")
    assert len(log) == 1
    assert log[0]["status"] == 200


def test_cross_tenant_rejected():
    gw = _setup_gateway()
    # valid-key-123 is registered for slack-ext, not pub-ext
    gw.register_route(GatewayRoute("/api/ext/other", "other-ext", ["GET"]))
    resp = gw.handle_request(GatewayRequest("GET", "/api/ext/other/data", api_key="valid-key-123"))
    assert resp.status_code == 403
    assert "not authorized" in resp.body["error"]
