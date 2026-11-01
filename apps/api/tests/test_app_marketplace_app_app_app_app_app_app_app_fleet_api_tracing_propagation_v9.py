from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_tracing_propagation_v9 import fleet_api_tracing_propagation_v9
def test_atp_v9():
    r = fleet_api_tracing_propagation_v9([{"propagation_enabled": True, "format": "w3c"}])
    assert r["w3c"] == 1
    assert r["healthy"]
