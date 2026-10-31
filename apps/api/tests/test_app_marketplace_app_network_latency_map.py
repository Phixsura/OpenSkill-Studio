from app.services.app_marketplace_app_network_latency_map import get_latency_map, find_optimal_region

def test_map():
    r = get_latency_map()
    assert r["total_regions"] == 4
    assert len(r["edges"]) == 6

def test_optimal():
    r = find_optimal_region(user_region="us-east")
    assert r["optimal"] == "us-east"  # 0ms to self
    assert r["latency_ms"] == 0

def test_unknown():
    r = find_optimal_region(user_region="mars")
    assert "error" in r
