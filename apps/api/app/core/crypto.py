"""Credential envelope encryption (Fernet).

Credentials are encrypted at rest and decrypted ONLY by the workflow executor
immediately before a provider call. No API endpoint ever returns decrypted
values (ADR-011 / R3).
"""

import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings
from app.exceptions import AppError


def _fernet() -> Fernet:
    key = settings.credential_encryption_key
    if not key:
        # Dev fallback: derive a stable key from the JWT secret so local
        # development works without extra setup. Production requires an
        # explicit CREDENTIAL_ENCRYPTION_KEY (validated in config.py).
        key = settings.jwt_secret
    # Accept either a proper 32-byte urlsafe-b64 Fernet key or any string
    # (derived via SHA-256 for convenience)
    try:
        return Fernet(key.encode())
    except (ValueError, Exception):
        derived = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        return Fernet(derived)


def encrypt_credentials(data: dict[str, str]) -> str:
    """Encrypt a {field_name: value} dict to an opaque token."""
    return _fernet().encrypt(json.dumps(data).encode()).decode()


def decrypt_credentials(token: str) -> dict[str, str]:
    """Decrypt a credential token. Raises AppError on tamper/corruption."""
    try:
        return json.loads(_fernet().decrypt(token.encode()).decode())
    except (InvalidToken, ValueError) as exc:
        raise AppError(
            "CREDENTIAL_DECRYPT_FAILED",
            "Stored credential could not be decrypted",
            500,
        ) from exc
