"""Config encryption — encrypt sensitive config values at rest."""

import hashlib
import base64


def encrypt_value(*, value: str, key: str) -> dict:
    # Simplified XOR-based encryption for demo (production would use AES-GCM)
    key_bytes = hashlib.sha256(key.encode()).digest()
    value_bytes = value.encode()
    encrypted = bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(value_bytes))
    encoded = base64.b64encode(encrypted).decode()
    return {"encrypted": encoded, "algorithm": "xor-sha256", "key_hash": hashlib.sha256(key.encode()).hexdigest()[:8]}


def decrypt_value(*, encrypted: str, key: str) -> str:
    key_bytes = hashlib.sha256(key.encode()).digest()
    encrypted_bytes = base64.b64decode(encrypted)
    decrypted = bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(encrypted_bytes))
    return decrypted.decode()


def identify_sensitive_fields(*, config: dict) -> list[str]:
    sensitive_patterns = {"password", "secret", "key", "token", "credential", "api_key", "private"}
    return [k for k in config.keys() if any(p in k.lower() for p in sensitive_patterns)]


def encrypt_config(*, config: dict, encryption_key: str) -> dict:
    sensitive = identify_sensitive_fields(config=config)
    result = dict(config)
    encrypted_fields = []
    for field in sensitive:
        if isinstance(result[field], str):
            enc = encrypt_value(value=result[field], key=encryption_key)
            result[field] = f"encrypted:{enc['encrypted']}"
            encrypted_fields.append(field)
    return {"config": result, "encrypted_fields": encrypted_fields, "total_encrypted": len(encrypted_fields)}
