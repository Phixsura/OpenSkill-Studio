from app.services.app_marketplace_app_app_app_app_app_app_app_config_encrypt import (
    generate_key, encrypt_value, decrypt_value, encrypt_config,
)

def test_encrypt_decrypt():
    key = generate_key()
    e = encrypt_value("my-secret-value", key)
    assert e["encrypted"]
    assert e["ciphertext"] != "my-secret-value"
    d = decrypt_value(e["ciphertext"], key)
    assert d["value"] == "my-secret-value"

def test_config():
    key = generate_key()
    r = encrypt_config({"db_host": "localhost", "db_pass": "secret", "port": 5432},
                         key, ["db_pass"])
    assert r["encrypted_fields"] == 1
    assert r["config"]["db_host"] == "localhost"
    assert r["config"]["db_pass"] != "secret"
    assert r["config"]["port"] == 5432
