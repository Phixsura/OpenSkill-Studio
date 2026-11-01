from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_type_safety import fleet_type_safety
def test_types():
    r = fleet_type_safety([{"strict_types": True, "type_coverage_pct": 95}, {"strict_types": False, "type_coverage_pct": 60}])
    assert r["strict_typed"] == 1
    assert r["avg_coverage_pct"] == 77.5
    assert not r["type_safe"]
