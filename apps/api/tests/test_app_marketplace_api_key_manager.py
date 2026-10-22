from app.services.app_marketplace_api_key_manager import generate_api_key, rotate_key, validate_key, mask_key

def test_generate():
    k = generate_api_key(app_id="a1", name="prod", scopes=["read"])
    assert k["raw_key"].startswith("osk_")
    assert len(k["key_hash"]) == 64
    assert k["status"] == "active"

def test_validate():
    k = generate_api_key(app_id="a1", name="test", scopes=[])
    assert validate_key(raw_key=k["raw_key"], stored_hash=k["key_hash"])
    assert not validate_key(raw_key="wrong", stored_hash=k["key_hash"])

def test_rotate():
    old = generate_api_key(app_id="a1", name="prod", scopes=["read"])
    r = rotate_key(old_key=old)
    assert r["new_key"]["raw_key"] != old["raw_key"]
    assert r["grace_period_hours"] == 24

def test_mask():
    assert mask_key(prefix="osk_abcd") == "osk_abcd" + "•" * 40
