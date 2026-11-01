from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_shape import apply_shaping, shaping_summary

def test_shaping():
    r = apply_shaping("api", "db", [
        {"source": "api", "destination": "db", "type": "delay", "delay_ms": 100},
        {"source": "api", "destination": "db", "type": "rate_limit", "rps": 50},
        {"source": "web", "destination": "api", "type": "delay", "delay_ms": 50},
    ])
    assert r["shaped"]
    assert len(r["effects"]) == 2

def test_summary():
    r = shaping_summary([
        {"type": "delay", "active": True},
        {"type": "delay", "active": True},
        {"type": "abort", "active": False},
    ])
    assert r["total_rules"] == 3
    assert r["active"] == 2
    assert r["by_type"]["delay"] == 2
