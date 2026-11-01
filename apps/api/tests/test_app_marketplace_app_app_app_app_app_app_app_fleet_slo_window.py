from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_slo_window import fleet_slo_burn_window
def test_burn():
    r = fleet_slo_burn_window({"target": 0.999, "errors": 2, "total": 1000})
    assert r["burn_rate"] == 2.0
    assert r["alert"]
