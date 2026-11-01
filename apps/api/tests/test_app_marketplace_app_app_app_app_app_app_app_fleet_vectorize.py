from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vectorize import fleet_vectorize_status
def test_vz():
    r = fleet_vectorize_status([{"active": True, "vectors": 5000000, "queries_24h": 1000000}])
    assert r["vectors"] == 5000000
    assert r["all_active"]
