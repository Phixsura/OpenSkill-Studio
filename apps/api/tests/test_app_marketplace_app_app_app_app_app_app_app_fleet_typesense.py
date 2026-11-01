from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_typesense import fleet_typesense_status
def test_ts():
    r = fleet_typesense_status([{"healthy": True, "collections": 20, "documents": 10000000}])
    assert r["documents"] == 10000000
    assert r["all_healthy"]
