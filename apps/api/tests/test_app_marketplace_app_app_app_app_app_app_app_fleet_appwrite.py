from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_appwrite import fleet_appwrite_status
def test_aw():
    r = fleet_appwrite_status([{"active": True, "databases": 5, "storage_gb": 50, "functions": 20}])
    assert r["databases"] == 5
    assert r["functions"] == 20
