from app.services.app_marketplace_app_app_app_app_app_app_app_key_rotation import KeyRotationScheduler

def test_rotation():
    s = KeyRotationScheduler()
    s.register_key("k1", rotation_days=30)
    c = s.check_rotation("k1", now=s._keys["k1"]["created"] + 86400 * 10)
    assert not c["due"]
    assert c["urgency"] == "ok"
    c2 = s.check_rotation("k1", now=s._keys["k1"]["created"] + 86400 * 31)
    assert c2["due"]
    r = s.rotate("k1")
    assert r["rotated"]
    assert r["rotations"] == 1
    assert s.summary()["total_keys"] == 1
