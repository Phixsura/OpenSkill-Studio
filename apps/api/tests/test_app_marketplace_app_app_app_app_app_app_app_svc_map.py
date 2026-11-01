from app.services.app_marketplace_app_app_app_app_app_app_app_svc_map import generate_service_map, detect_hotspots

def test_map():
    r = generate_service_map([
        {"source": "gateway", "destination": "api", "request_count": 10000},
        {"source": "api", "destination": "db", "request_count": 5000},
        {"source": "api", "destination": "cache", "request_count": 8000},
    ])
    assert r["node_count"] == 4
    assert r["entry_points"] == ["gateway"]
    assert sorted(r["leaf_nodes"]) == ["cache", "db"]

def test_hotspots():
    edges = [{"source": "a", "destination": "b", "requests": 500, "error_rate": 1},
             {"source": "c", "destination": "d", "requests": 2000, "error_rate": 10}]
    r = detect_hotspots(edges, threshold_rps=1000)
    assert len(r) == 1
    assert r[0]["source"] == "c"
