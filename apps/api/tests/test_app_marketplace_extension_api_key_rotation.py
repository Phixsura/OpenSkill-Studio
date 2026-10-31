from app.services.app_marketplace_extension_api_key_rotation import ExtApiKeyRotationService

def test_create_and_validate():
    svc = ExtApiKeyRotationService()
    raw, key = svc.create("ext-1", "Production", ["read", "write"])
    assert raw.startswith("osk_")
    result = svc.validate(raw)
    assert result is not None
    assert result.name == "Production"

def test_rotate():
    svc = ExtApiKeyRotationService()
    raw, old_key = svc.create("ext-1", "Key", ["read"])
    result = svc.rotate(old_key.key_id)
    assert result is not None
    new_raw, new_key = result
    # Old key still valid during grace
    assert svc.validate(raw) is not None
    assert svc.validate(new_raw) is not None

def test_revoke():
    svc = ExtApiKeyRotationService()
    raw, key = svc.create("ext-1", "Key", [])
    svc.revoke(key.key_id)
    assert svc.validate(raw) is None

def test_invalid_key():
    svc = ExtApiKeyRotationService()
    assert svc.validate("osk_invalid") is None
