from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mimir import fleet_mimir_status
def test_mimir():
    r = fleet_mimir_status([{"healthy": True, "active_series": 5000000, "samples_per_sec": 100000}])
    assert r["total_series"] == 5000000
    assert r["all_healthy"]
