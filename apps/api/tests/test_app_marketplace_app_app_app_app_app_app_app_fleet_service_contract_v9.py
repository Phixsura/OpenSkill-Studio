from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_contract_v9 import fleet_service_contract_v9
def test_scon_v9():
    r = fleet_service_contract_v9([{"compliant": True, "sla_met": True, "penalty_amount": 0}])
    assert r["penalties"] == 0
    assert r["healthy"]
