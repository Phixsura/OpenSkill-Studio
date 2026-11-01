from app.services.app_marketplace_app_app_app_app_app_app_app_api_key_mgr import generate_key, validate_key, rotate_keys
import time

def test_generate():
    r = generate_key("test")
    assert r["key"].startswith("test_")
    assert len(r["key_hash"]) == 64

def test_validate():
    r = generate_key()
    v = validate_key(r["key"], r["key_hash"])
    assert v["valid"]
    v2 = validate_key("wrong_key", r["key_hash"])
    assert not v2["valid"]

def test_rotate():
    now = time.time()
    r = rotate_keys([
        {"id": "k1", "created_at": now - 86400 * 100},
        {"id": "k2", "created_at": now - 86400 * 10},
    ], max_age_days=90)
    assert r["to_rotate"] == 1
    assert r["active"] == 1
