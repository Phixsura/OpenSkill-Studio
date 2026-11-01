from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hpa import fleet_hpa_status
def test_hpa():
    r = fleet_hpa_status([{"current": 10, "max": 10, "min": 1}, {"current": 3, "max": 10, "min": 1}])
    assert r["at_max"] == 1
    assert r["scaling_pressure"]
