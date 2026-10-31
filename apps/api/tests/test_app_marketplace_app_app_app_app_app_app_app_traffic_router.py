from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_router import (
    create_route, resolve_target, build_routing_table,
)

def test_route():
    r = create_route("/api", [{"backend": "v1", "weight": 9}, {"backend": "v2", "weight": 1}])
    assert r["target_count"] == 2
    assert r["targets"][0]["weight"] == 90.0

def test_resolve():
    r = create_route("/api", [{"backend": "A", "weight": 1}, {"backend": "B", "weight": 1}])
    t = resolve_target(r, "req_123")
    assert t in ("A", "B")

def test_table():
    routes = [create_route("/api", [{"backend": "v1"}]), create_route("/web", [{"backend": "v2"}])]
    t = build_routing_table(routes)
    assert t["route_count"] == 2
    assert "/api" in t["paths"]
