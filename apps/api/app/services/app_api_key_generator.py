"""API key generator — secure key generation with prefix and hashing."""

import hashlib
import secrets


PREFIX = "osk_app_"
KEY_BYTES = 32  # 256 bits


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key.
    
    Returns (raw_key, key_prefix, key_hash):
    - raw_key: Full key shown once to the user
    - key_prefix: First 12 chars for identification  
    - key_hash: SHA-256 hash stored in DB
    """
    random_part = secrets.token_urlsafe(KEY_BYTES)
    raw_key = f"{PREFIX}{random_part}"
    key_prefix = raw_key[:12]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_prefix, key_hash


def hash_api_key(raw_key: str) -> str:
    """Hash a raw API key for storage/lookup."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """Verify a raw key matches a stored hash."""
    return secrets.compare_digest(hash_api_key(raw_key), stored_hash)


def is_valid_key_format(key: str) -> bool:
    """Check if a string looks like a valid API key."""
    return key.startswith(PREFIX) and len(key) >= len(PREFIX) + 20
