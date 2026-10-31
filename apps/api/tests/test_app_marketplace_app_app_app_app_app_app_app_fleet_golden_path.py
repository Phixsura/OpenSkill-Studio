from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_golden_path import fleet_golden_path
def test_gp():
    r = fleet_golden_path([{"uses_golden_path": True}] * 7 + [{"uses_golden_path": False}] * 3)
    assert r["on_golden_path"] == 7
    assert r["adoption_pct"] == 70.0
