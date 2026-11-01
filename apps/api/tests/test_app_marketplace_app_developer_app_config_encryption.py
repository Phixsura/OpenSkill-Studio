from app.services.app_marketplace_app_developer_app_config_encryption import encrypt_value, decrypt_value, identify_sensitive_fields, encrypt_config

def test_encrypt_decrypt():
    enc = encrypt_value(value="my-secret-value", key="master-key")
    dec = decrypt_value(encrypted=enc["encrypted"], key="master-key")
    assert dec == "my-secret-value"

def test_different_keys_different_output():
    enc1 = encrypt_value(value="test", key="key1")
    enc2 = encrypt_value(value="test", key="key2")
    assert enc1["encrypted"] != enc2["encrypted"]

def test_identify():
    config = {"db_password": "x", "api_key": "y", "app_name": "z", "secret_token": "w"}
    r = identify_sensitive_fields(config=config)
    assert "db_password" in r
    assert "api_key" in r
    assert "app_name" not in r

def test_encrypt_config():
    config = {"db_password": "secret123", "app_name": "MyApp", "api_key": "key456"}
    r = encrypt_config(config=config, encryption_key="master")
    assert r["total_encrypted"] == 2
    assert r["config"]["db_password"].startswith("encrypted:")
    assert r["config"]["app_name"] == "MyApp"
