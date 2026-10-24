from app.services.app_marketplace_app_app_app_app_app_app_app_data_encrypt import DataEncryptionManager

def test_create_rotate():
    dem = DataEncryptionManager()
    r = dem.create_key("primary", "AES-256-GCM")
    assert r["algorithm"] == "AES-256-GCM"
    fp1 = r["fingerprint"]
    r2 = dem.rotate_key("primary")
    assert r2["version"] == 2
    assert r2["new_fingerprint"] != fp1

def test_active():
    dem = DataEncryptionManager()
    dem.create_key("k1")
    dem.create_key("k2")
    dem.set_active("k2")
    assert dem.stats()["active_key"] == "k2"
