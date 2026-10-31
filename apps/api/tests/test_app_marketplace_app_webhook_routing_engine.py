from app.services.app_marketplace_app_webhook_routing_engine import create_routing_rule, route_event, build_routing_table

def test_create():
    r = create_routing_rule(event_type="app.installed", endpoint_url="https://x.com/hook", priority=10)
    assert r["active"]

def test_invalid_priority():
    r = create_routing_rule(event_type="x", endpoint_url="y", priority=200)
    assert r["error"]

def test_route():
    rules = [
        {"event_type": "app.installed", "endpoint_url": "https://a.com", "priority": 5, "active": True},
        {"event_type": "app.installed", "endpoint_url": "https://b.com", "priority": 10, "active": True},
        {"event_type": "app.updated", "endpoint_url": "https://c.com", "priority": 1, "active": True},
    ]
    r = route_event(event_type="app.installed", rules=rules)
    assert len(r) == 2
    assert r[0]["endpoint_url"] == "https://b.com"  # highest priority first

def test_table():
    rules = [{"event_type": "a", "endpoint_url": "u1", "priority": 0},
             {"event_type": "a", "endpoint_url": "u2", "priority": 1},
             {"event_type": "b", "endpoint_url": "u3", "priority": 0}]
    t = build_routing_table(rules=rules)
    assert len(t["event_types"]) == 2
    assert t["total_rules"] == 3
