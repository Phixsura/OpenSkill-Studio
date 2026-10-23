"""Config encryption — encrypt sensitive config values at rest."""
from __future__ import annotations
import hashlib
import base64
import secrets


def generate_key() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()


def encrypt_value(value: str, key: str) -> dict:
    key_bytes = base64.urlsafe_b64decode(key.encode())
    xor_key = hashlib.sha256(key_bytes).digest()
    encrypted = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(value.encode()))
    ciphertext = base64.urlsafe_b64encode(encrypted).decode()
    return {"encrypted": True, "ciphertext": ciphertext, "algorithm": "xor-sha256"}


def decrypt_value(ciphertext: str, key: str) -> dict:
    key_bytes = base64.urlsafe_b64decode(key.encode())
    xor_key = hashlib.sha256(key_bytes).digest()
    encrypted = base64.urlsafe_b64decode(ciphertext.encode())
    decrypted = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(encrypted))
    return {"decrypted": True, "value": decrypted.decode()}


def encrypt_config(config: dict, key: str, fields: list[str]) -> dict:
    result = {}
    encrypted_count = 0
    for k, v in config.items():
        if k in fields and isinstance(v, str):
            result[k] = encrypt_value(v, key)["ciphertext"]
            encrypted_count += 1
        else:
            result[k] = v
    return {"config": result, "encrypted_fields": encrypted_count}
