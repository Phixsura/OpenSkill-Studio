from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_edge_inf import fleet_ai_edge_inference
def test_ei():
    r = fleet_ai_edge_inference([{"active": True, "location": "us-east", "requests_24h": 10000000, "p50_ms": 8}])
    assert r["locations"] == 1
    assert r["fast"]
