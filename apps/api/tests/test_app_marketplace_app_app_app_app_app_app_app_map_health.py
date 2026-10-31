from app.services.app_marketplace_app_app_app_app_app_app_app_map_health import overlay_health

def test_overlay():
    r = overlay_health(
        [{"name": "api", "health": "healthy"}, {"name": "db", "health": "degraded"}],
        [{"source": "api", "destination": "db", "latency_ms": 5}])
    assert r["healthy_nodes"] == 1
    assert r["edges"][0]["edge_health"] == "degraded"
