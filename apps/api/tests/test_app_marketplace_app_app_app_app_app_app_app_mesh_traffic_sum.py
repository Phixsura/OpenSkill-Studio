from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_traffic_sum import mesh_traffic_summary

def test_summary():
    r = mesh_traffic_summary([
        {"source": "web", "destination": "api", "rps": 1000, "requests": 60000, "errors": 60, "protocol": "HTTP/2"},
        {"source": "api", "destination": "db", "rps": 500, "requests": 30000, "errors": 10, "protocol": "gRPC"},
        {"source": "api", "destination": "cache", "rps": 800, "requests": 48000, "errors": 5, "protocol": "HTTP/2"},
    ])
    assert r["total_rps"] == 2300
    assert r["total_requests"] == 138000
    assert r["unique_flows"] == 3
    assert r["top_flows"][0]["source"] == "web"
    assert r["by_protocol"]["HTTP/2"] == 108000
