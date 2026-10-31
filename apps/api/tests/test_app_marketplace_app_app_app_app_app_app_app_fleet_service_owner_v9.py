from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_owner_v9 import fleet_service_owner_v9
def test_so_v9():
    r = fleet_service_owner_v9([{"owner": "team-a", "oncall": True, "runbook": True}])
    assert r["with_owner"] == 1
    assert r["healthy"]
