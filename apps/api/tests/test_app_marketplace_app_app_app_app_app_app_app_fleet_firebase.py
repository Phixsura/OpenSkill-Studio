from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_firebase import fleet_firebase_status
def test_fb():
    r = fleet_firebase_status([{"active": True, "auth_users": 500000, "firestore_docs": 10000000, "storage_gb": 100}])
    assert r["auth_users"] == 500000
    assert r["firestore_docs"] == 10000000
