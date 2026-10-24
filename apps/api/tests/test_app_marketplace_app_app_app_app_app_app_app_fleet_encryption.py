from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_encryption import fleet_encryption_status
def test_enc():
    r = fleet_encryption_status([{"encryption_at_rest": True, "encryption_in_transit": True}, {"encryption_at_rest": True, "encryption_in_transit": False}])
    assert r["both"] == 1
    assert not r["fully_encrypted"]
