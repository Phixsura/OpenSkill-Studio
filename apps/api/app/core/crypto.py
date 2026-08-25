"""Credential envelope encryption (Fernet).

Credentials are encrypted at rest and decrypted ONLY by the workflow executor
immediately before a provider call. No API endpoint ever returns decrypted
values (ADR-011 / R3).

Key policy:
- CREDENTIAL_ENCRYPTION_KEY may hold one or more comma-separated Fernet keys
  (32-byte urlsafe base64). The FIRST key encrypts; all keys decrypt
  (MultiFernet) — rotate by prepending a new key and re-encrypting lazily.
- An invalid-format key fails fast with a clear error. It must NOT silently
  fall back to a derived key: that would switch the effective key and brick
  every stored credential with CREDENTIAL_DECRYPT_FAILED at execution time.
- Empty key: derive from the JWT secret in development/test only (local
  convenience). Production requires an explicit key (validated in config.py).
"""

import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from app.config import settings
from app.exceptions import AppError


def _fernet() -> MultiFernet:
    raw = settings.credential_encryption_key
    if not raw:
        # Dev/test fallback: derive a stable key from the JWT secret so local
        # development works without extra setup. config.py rejects an empty
        # CREDENTIAL_ENCRYPTION_KEY outside development/test.
        derived = base64.urlsafe_b64encode(
            hashlib.sha256(settings.jwt_secret.encode()).digest()
        )
        return MultiFernet([Fernet(derived)])

    fernets: list[Fernet] = []
    for idx, key in enumerate(k.strip() for k in raw.split(",")):
        try:
            fernets.append(Fernet(key.encode()))
        except ValueError as exc:
            # Fail fast: a silently derived substitute key would encrypt new
            # credentials under a different key than the operator intended
            # and make every previously stored credential undecryptable.
            raise AppError(
                "CREDENTIAL_KEY_INVALID",
                f"CREDENTIAL_ENCRYPTION_KEY entry {idx + 1} is not a valid Fernet key "
                "(expected 32-byte urlsafe base64)",
                500,
            ) from exc
    return MultiFernet(fernets)


def encrypt_credentials(data: dict[str, str]) -> str:
    """Encrypt a {field_name: value} dict to an opaque token (primary key)."""
    return _fernet().encrypt(json.dumps(data).encode()).decode()


def decrypt_credentials(token: str) -> dict[str, str]:
    """Decrypt a credential token (tries all configured keys).

    Raises AppError on tamper/corruption.
    """
    try:
        return json.loads(_fernet().decrypt(token.encode()).decode())
    except (InvalidToken, ValueError) as exc:
        raise AppError(
            "CREDENTIAL_DECRYPT_FAILED",
            "Stored credential could not be decrypted",
            500,
        ) from exc
