from app.services.app_marketplace_extension_key_rotation import (
    KeyRotationService,
)


def test_generate_and_validate():
    svc = KeyRotationService()
    result = svc.generate("ext-1")
    assert result["api_key"].startswith("sk_")
    v = svc.validate(result["api_key"])
    assert v["valid"] is True


def test_invalid_key():
    svc = KeyRotationService()
    v = svc.validate("fake_key")
    assert v["valid"] is False


def test_rotate():
    svc = KeyRotationService()
    old = svc.generate("ext-1")
    result = svc.rotate("ext-1", reason="scheduled")
    assert result["grace_keys"] == 1
    # Old key still valid during grace
    v = svc.validate(old["api_key"])
    assert v["valid"] is True
    assert v["status"] == "grace"
    # New key also valid
    v2 = svc.validate(result["new_key"]["api_key"])
    assert v2["valid"] is True


def test_revoke():
    svc = KeyRotationService()
    result = svc.generate("ext-1")
    assert svc.revoke(result["key_id"]) is True
    v = svc.validate(result["api_key"])
    assert v["valid"] is False
    assert "revoked" in v["reason"].lower()


def test_revoke_all():
    svc = KeyRotationService()
    svc.generate("ext-1")
    svc.generate("ext-1")
    svc.generate("ext-2")
    count = svc.revoke_all("ext-1")
    assert count == 2


def test_active_keys():
    svc = KeyRotationService()
    svc.generate("ext-1")
    svc.rotate("ext-1")
    active = svc.get_active_keys("ext-1")
    assert len(active) == 2  # new active + old grace


def test_key_hash_stored():
    svc = KeyRotationService()
    result = svc.generate("ext-1")
    key = svc._keys[result["key_id"]]
    assert "sk_" not in key.key_hash  # hash, not raw
    assert len(key.key_hash) == 64


def test_rotation_history():
    svc = KeyRotationService()
    svc.generate("ext-1")
    svc.rotate("ext-1", "security")
    history = svc.get_rotation_history("ext-1")
    assert len(history) == 1
    assert history[0].reason == "security"
