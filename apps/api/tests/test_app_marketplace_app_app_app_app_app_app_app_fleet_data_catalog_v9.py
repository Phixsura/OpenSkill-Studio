from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_catalog_v9 import fleet_data_catalog_v9
def test_dc_v9():
    r = fleet_data_catalog_v9([{"cataloged": True, "lineage": True, "owner": "data-team"}])
    assert r["cataloged"] == 1
    assert r["healthy"]
