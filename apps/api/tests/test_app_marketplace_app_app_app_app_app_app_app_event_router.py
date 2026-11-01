from app.services.app_marketplace_app_app_app_app_app_app_app_event_router import (
    add_route, route_event, router_stats, clear_routes,
)

def test_routing():
    clear_routes()
    add_route("user.*", "user_handler")
    add_route("order.created", "order_handler")
    add_route("#", "audit_handler")  # catch-all
    r = route_event("user.created")
    assert r["routed"]
    assert r["handler_count"] == 2  # user_handler + audit
    r2 = route_event("order.created")
    assert r2["handler_count"] == 2  # order_handler + audit
    clear_routes()

def test_stats():
    clear_routes()
    add_route("a.*", "h1")
    route_event("a.b")
    s = router_stats()
    assert s["total_routes"] == 1
    assert s["routes"][0]["hits"] == 1
    clear_routes()
