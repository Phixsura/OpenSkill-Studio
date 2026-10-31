from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_htmx import fleet_htmx_status
def test_htmx():
    r = fleet_htmx_status([{"active": True, "swaps_24h": 500000, "avg_swap_ms": 30}])
    assert r["swaps_24h"] == 500000
    assert r["snappy"]
