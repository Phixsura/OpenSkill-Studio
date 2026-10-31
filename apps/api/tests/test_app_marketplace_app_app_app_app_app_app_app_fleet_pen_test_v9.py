from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pen_test_v9 import fleet_pen_test_v9
def test_pt_v9():
    r = fleet_pen_test_v9([{"remediated": True, "severity": "high"}, {"remediated": True, "severity": "medium"}])
    assert r["remediated"] == 2
    assert r["healthy"]
