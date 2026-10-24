from app.services.app_marketplace_app_app_app_app_app_app_app_gw_router import GatewayRouter

def test_path_match():
    gr = GatewayRouter()
    gr.add_route("/api/v1", "api-v1")
    gr.add_route("/api/v2", "api-v2")
    r = gr.match("/api/v2/users")
    assert r["matched"]
    assert r["backend"] == "api-v2"

def test_header_match():
    gr = GatewayRouter()
    gr.add_route("/api", "canary", header_match={"X-Canary": "true"})
    gr.add_route("/api", "stable")
    r = gr.match("/api/users", headers={"X-Canary": "true"})
    assert r["backend"] == "canary"

def test_no_match():
    gr = GatewayRouter()
    gr.add_route("/api", "api")
    r = gr.match("/health")
    assert not r["matched"]
