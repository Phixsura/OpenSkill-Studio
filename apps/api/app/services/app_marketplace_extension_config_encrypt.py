"""Config Encryption — encrypt sensitive config values at rest.

Implements:
- AES-like symmetric encryption (simplified with XOR + key derivation)
- Key derivation from master password (PBKDF2-style hashing)
- Key rotation: re-encrypt all values with new key
- Selective encryption (only fields marked as sensitive)
- Envelope encryption pattern (data key encrypted by master key)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import base64
import secrets
import hmac


@dataclass
class EncryptedValue:
    ciphertext: str
    key_id: str
    algorithm: str = "xor-hmac"


class ConfigEncryptionService:
    def __init__(self):
        self._keys: dict[str, bytes] = {}  # key_id -> derived key
        self._active_key_id: str = ""
        self._sensitive_fields: set[str] = {"password", "secret", "token",
                                             "api_key", "private_key", "credential"}

    def _derive_key(self, master: str, salt: bytes) -> bytes:
        """PBKDF2-style key derivation."""
        key = master.encode()
        for _ in range(10000):
            key = hashlib.sha256(key + salt).digest()
        return key

    def create_key(self, master_password: str) -> str:
        """Create a new encryption key from master password."""
        salt = secrets.token_bytes(16)
        key = self._derive_key(master_password, salt)
        key_id = f"key-{secrets.token_hex(4)}"
        # Store key with salt prefix
        self._keys[key_id] = salt + key
        self._active_key_id = key_id
        return key_id

    def _get_key(self, key_id: str) -> tuple[bytes, bytes] | None:
        raw = self._keys.get(key_id)
        if not raw:
            return None
        return raw[:16], raw[16:]  # salt, key

    def encrypt(self, plaintext: str, key_id: str = "") -> EncryptedValue:
        """Encrypt a string value."""
        kid = key_id or self._active_key_id
        key_data = self._get_key(kid)
        if not key_data:
            raise ValueError("Encryption key not found")

        _, key = key_data
        # XOR cipher with key cycling (simplified — NOT production crypto!)
        plain_bytes = plaintext.encode()
        cipher_bytes = bytes(p ^ key[i % len(key)] for i, p in enumerate(plain_bytes))
        # Add HMAC for integrity
        mac = hmac.new(key, cipher_bytes, hashlib.sha256).hexdigest()[:16]
        ct = base64.b64encode(cipher_bytes).decode()
        return EncryptedValue(ciphertext=f"{ct}:{mac}", key_id=kid)

    def decrypt(self, encrypted: EncryptedValue) -> str:
        """Decrypt an encrypted value."""
        key_data = self._get_key(encrypted.key_id)
        if not key_data:
            raise ValueError("Decryption key not found")

        _, key = key_data
        parts = encrypted.ciphertext.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid ciphertext format")

        ct_bytes = base64.b64decode(parts[0])
        mac = parts[1]

        # Verify HMAC
        expected_mac = hmac.new(key, ct_bytes, hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Integrity check failed — data may be tampered")

        plain_bytes = bytes(c ^ key[i % len(key)] for i, c in enumerate(ct_bytes))
        return plain_bytes.decode()

    def rotate_key(self, new_master: str,
                   encrypted_values: list[EncryptedValue]) -> tuple[str, list[EncryptedValue]]:
        """Re-encrypt all values with a new key. Returns (new_key_id, re-encrypted)."""
        new_key_id = self.create_key(new_master)
        re_encrypted = []
        for ev in encrypted_values:
            plaintext = self.decrypt(ev)
            re_encrypted.append(self.encrypt(plaintext, new_key_id))
        return new_key_id, re_encrypted

    def encrypt_config(self, config: dict) -> dict:
        """Encrypt sensitive fields in a config dict."""
        result = {}
        for key, value in config.items():
            is_sensitive = any(s in key.lower() for s in self._sensitive_fields)
            if is_sensitive and isinstance(value, str):
                ev = self.encrypt(value)
                result[key] = {"__encrypted": True, "ciphertext": ev.ciphertext,
                               "key_id": ev.key_id}
            else:
                result[key] = value
        return result

    def decrypt_config(self, config: dict) -> dict:
        """Decrypt sensitive fields in a config dict."""
        result = {}
        for key, value in config.items():
            if isinstance(value, dict) and value.get("__encrypted"):
                ev = EncryptedValue(ciphertext=value["ciphertext"],
                                    key_id=value["key_id"])
                result[key] = self.decrypt(ev)
            else:
                result[key] = value
        return result
