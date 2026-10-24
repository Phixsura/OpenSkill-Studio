from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_immutable_infra_v9 import fleet_immutable_infra_v9
def test_ii_v9():
    r = fleet_immutable_infra_v9([{"immutable": True, "age_hours": 48}])
    assert r["immutable"] == 1
    assert r["mutable"] == 0
    assert r["healthy"]
