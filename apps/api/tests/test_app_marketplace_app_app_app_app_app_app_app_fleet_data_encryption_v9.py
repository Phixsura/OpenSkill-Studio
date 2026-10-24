from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_encryption_v9 import fleet_data_encryption_v9
def test_de_v9():
    r = fleet_data_encryption_v9([{"encrypted_at_rest": True, "encrypted_in_transit": True, "key_rotated_recently": True}])
    assert r["encrypted_at_rest"] == 1
    assert r["healthy"]
