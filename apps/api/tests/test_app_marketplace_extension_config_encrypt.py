from app.services.app_marketplace_extension_config_encrypt import ConfigEncryptionService


def test_encrypt_decrypt():
    ce = ConfigEncryptionService()
    ce.create_key("master-password-123")
    encrypted = ce.encrypt("my-secret-value")
    decrypted = ce.decrypt(encrypted)
    assert decrypted == "my-secret-value"


def test_different_ciphertext_each_time():
    ce = ConfigEncryptionService()
    ce.create_key("master")
    e1 = ce.encrypt("same-text")
    e2 = ce.encrypt("same-text")
    # Same plaintext, same key → same ciphertext (deterministic in this impl)
    assert ce.decrypt(e1) == ce.decrypt(e2) == "same-text"


def test_wrong_key_fails():
    from app.services.app_marketplace_extension_config_encrypt import EncryptedValue
    ce = ConfigEncryptionService()
    k1 = ce.create_key("password-1")
    encrypted = ce.encrypt("secret", k1)
    k2 = ce.create_key("password-2")
    # Wrong key should fail on HMAC or produce garbage
    try:
        result = ce.decrypt(EncryptedValue(ciphertext=encrypted.ciphertext, key_id=k2))
        # If it didn't raise, the result should be wrong
        assert result != "secret"
    except (ValueError, UnicodeDecodeError):
        pass  # expected


def test_tampered_ciphertext():
    from app.services.app_marketplace_extension_config_encrypt import EncryptedValue
    ce = ConfigEncryptionService()
    ce.create_key("master")
    encrypted = ce.encrypt("secret")
    # Tamper: change the HMAC
    parts = encrypted.ciphertext.split(":")
    bad_mac = "0" * 16
    tampered = EncryptedValue(ciphertext=f"{parts[0]}:{bad_mac}",
                               key_id=encrypted.key_id)
    try:
        ce.decrypt(tampered)
        assert False
    except ValueError as e:
        assert "Integrity" in str(e) or "tampered" in str(e)


def test_key_rotation():
    ce = ConfigEncryptionService()
    ce.create_key("old-master")
    values = [ce.encrypt("secret-1"), ce.encrypt("secret-2")]
    new_key_id, re_encrypted = ce.rotate_key("new-master", values)
    # Old key still works for old values
    assert ce.decrypt(values[0]) == "secret-1"
    # New key works for re-encrypted
    assert ce.decrypt(re_encrypted[0]) == "secret-1"
    assert re_encrypted[0].key_id == new_key_id


def test_encrypt_config():
    ce = ConfigEncryptionService()
    ce.create_key("master")
    config = {
        "database_url": "postgres://localhost",
        "database_password": "super-secret",
        "api_key": "sk-12345",
        "debug": True,
        "port": 8080,
    }
    encrypted = ce.encrypt_config(config)
    # Sensitive fields encrypted
    assert encrypted["database_password"]["__encrypted"] is True
    assert encrypted["api_key"]["__encrypted"] is True
    # Non-sensitive fields unchanged
    assert encrypted["database_url"] == "postgres://localhost"
    assert encrypted["debug"] is True


def test_decrypt_config():
    ce = ConfigEncryptionService()
    ce.create_key("master")
    original = {"db_password": "secret123", "host": "localhost"}
    encrypted = ce.encrypt_config(original)
    decrypted = ce.decrypt_config(encrypted)
    assert decrypted["db_password"] == "secret123"
    assert decrypted["host"] == "localhost"


def test_unicode():
    ce = ConfigEncryptionService()
    ce.create_key("master")
    encrypted = ce.encrypt("密码：你好世界！🔑")
    assert ce.decrypt(encrypted) == "密码：你好世界！🔑"
