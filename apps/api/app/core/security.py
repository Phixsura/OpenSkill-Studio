"""Password hashing and JWT token utilities."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from ulid import ULID

from app.config import settings

ALGORITHM = "HS256"


# ── Password ─────────────────────────────────────────────────


# bcrypt only ever consumes the first 72 BYTES of the password; bcrypt >=4.1
# (we run 5.0.0) RAISES ValueError on longer input instead of silently
# truncating. Our password policy allows up to 128 CHARACTERS
# (schemas/auth.py), and any multi-byte char pushes the byte count past 72
# well before that — so a policy-compliant password (e.g. 93 ASCII chars, or
# ~30 emoji) crashed hashpw/checkpw with an unhandled 500 on register / login /
# change-password / reset. Truncate to 72 bytes ourselves (the classic bcrypt
# pre-hash-length handling) so hashing is total over every accepted password.
# Truncation is on the ENCODED bytes and applied identically in hash + verify,
# so verification stays consistent; we slice bytes then drop any partial
# trailing multibyte char to keep .encode()/.decode() round-trips clean.
_BCRYPT_MAX_BYTES = 72


def _bcrypt_bytes(password: str) -> bytes:
    return password.encode()[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_bcrypt_bytes(password), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_bcrypt_bytes(plain), hashed.encode())


# ── JWT ──────────────────────────────────────────────────────


def create_access_token(user_id: str, email: str, role: str) -> str:
    now = datetime.now(UTC)
    # Note: email is accepted as parameter for signature compatibility
    # but NOT included in the JWT payload to avoid PII exposure.
    # The API resolves user details from sub (user_id) via DB lookup.
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "jti": str(ULID()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    """Return (raw_token, jti, expires_at)."""
    now = datetime.now(UTC)
    jti = str(ULID())
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": expires_at,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    return token, jti, expires_at


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises on expiry / invalid signature."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
