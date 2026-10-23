from app.services.app_marketplace_app_trusted_device import register_device, is_trusted, list_devices

def test_register():
    r = register_device(user_id="u1", device_name="MacBook Pro", device_fingerprint="abc123xyz")
    assert r["device_id"].startswith("dev_")
    assert r["trusted"]
    assert len(r["fingerprint_hash"]) == 16

def test_trusted():
    devices = [{"fingerprint_hash": "abc", "device_name": "Mac", "trusted_until": "2099-01-01T00:00:00"}]
    r = is_trusted(fingerprint_hash="abc", trusted_devices=devices)
    assert r["trusted"]
    assert r["skip_mfa"]

def test_untrusted():
    r = is_trusted(fingerprint_hash="unknown", trusted_devices=[])
    assert not r["trusted"]
    assert r["require_mfa"]

def test_list():
    devices = [{"trusted_until": "2099-01-01T00:00:00"}, {"trusted_until": "2020-01-01T00:00:00"}]
    r = list_devices(devices=devices)
    assert r["total"] == 1
