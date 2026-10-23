from app.services.app_marketplace_app_trusted_device import register_device, is_trusted, list_devices

def test_register():
    r = register_device(user_id="u1", device_name="MacBook Pro", device_fingerprint="abc123xyz")
    assert r["device_id"].startswith("dev_")
    assert r["trusted"]
    assert len(r["device_token"]) == 24

def test_trusted():
    reg = register_device(user_id="u1", device_name="Mac", device_fingerprint="fp1")
    devices = [{"device_token": reg["device_token"], "user_id": "u1",
                "device_name": "Mac", "trusted_until": "2099-01-01T00:00:00"}]
    r = is_trusted(device_token=reg["device_token"], user_id="u1", trusted_devices=devices)
    assert r["trusted"]
    assert r["skip_mfa"]

def test_untrusted():
    r = is_trusted(device_token="unknown", user_id="u1", trusted_devices=[])
    assert not r["trusted"]
    assert r["require_mfa"]

def test_wrong_user():
    reg = register_device(user_id="u1", device_name="Mac", device_fingerprint="fp1")
    devices = [{"device_token": reg["device_token"], "user_id": "u1",
                "device_name": "Mac", "trusted_until": "2099-01-01T00:00:00"}]
    r = is_trusted(device_token=reg["device_token"], user_id="u2", trusted_devices=devices)
    assert not r["trusted"]

def test_list():
    devices = [{"device_id": "d1", "device_name": "Mac", "device_token": "secret",
                "trusted_until": "2099-01-01T00:00:00"},
               {"device_id": "d2", "device_name": "Old", "device_token": "old",
                "trusted_until": "2020-01-01T00:00:00"}]
    r = list_devices(devices=devices)
    assert r["total"] == 1
    assert "device_token" not in r["devices"][0]  # token stripped
