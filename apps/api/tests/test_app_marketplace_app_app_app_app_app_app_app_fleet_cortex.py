from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cortex import fleet_cortex_status
def test_cortex():
    r = fleet_cortex_status([{"healthy": True, "active_series": 10000000, "samples_per_sec": 500000}])
    assert r["active_series"] == 10000000
    assert r["all_healthy"]
