from app.services.app_marketplace_app_api_gateway import create_route, match_route, build_gateway_config

def test_create():
    r = create_route(path_pattern="/api/v1/users", target_app_id="a1", methods=["get", "post"])
    assert r["methods"] == ["GET", "POST"]
    assert r["auth_required"]

def test_invalid_path():
    r = create_route(path_pattern="no-slash", target_app_id="a1", methods=["GET"])
    assert r["error"]

def test_match():
    routes = [create_route(path_pattern="/api/v1/users", target_app_id="a1", methods=["GET"]),
              create_route(path_pattern="/api/v1/apps", target_app_id="a2", methods=["POST"])]
    assert match_route(path="/api/v1/users", method="GET", routes=routes)["target_app_id"] == "a1"
    assert match_route(path="/api/v1/unknown", method="GET", routes=routes) is None

def test_config():
    routes = [create_route(path_pattern="/api", target_app_id="a1", methods=["GET"])]
    c = build_gateway_config(routes=routes)
    assert c["route_count"] == 1
    assert "auth" in c["middleware"]
