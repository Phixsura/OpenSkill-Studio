from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_governance_v9 import fleet_data_governance_v9
def test_dg_v9():
    r = fleet_data_governance_v9([{"classified": True, "has_pii": False, "encrypted": True}])
    assert r["classified"] == 1
    assert r["healthy"]
