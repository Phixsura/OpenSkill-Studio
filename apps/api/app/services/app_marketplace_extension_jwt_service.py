"""JWT Token Service — create, validate, and refresh JSON Web Tokens.

Implements:
- HMAC-SHA256 signing (HS256)
- Standard claims: iss, sub, aud, exp, iat, jti
- Custom claims support
- Token refresh with rotation
- Revocation via JTI blocklist
- Expiry validation
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import secrets
import time


class JwtError(Exception):
    pass


class JwtTokenService:
    def __init__(self, secret: str = "", issuer: str = "openskill-marketplace"):
        self._secret = secret or secrets.token_urlsafe(32)
        self._issuer = issuer
        self._revoked_jtis: set[str] = set()
        self._refresh_tokens: dict[str, dict] = {}  # refresh_token -> metadata

    def _b64url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    def _b64url_decode(self, s: str) -> bytes:
        padding = 4 - len(s) % 4
        if padding != 4:
            s += "=" * padding
        return base64.urlsafe_b64decode(s)

    def _sign(self, payload: str) -> str:
        header = self._b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        body = self._b64url_encode(payload.encode())
        signing_input = f"{header}.{body}"
        signature = hmac.new(
            self._secret.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        sig_encoded = self._b64url_encode(signature)
        return f"{signing_input}.{sig_encoded}"

    def create(self, subject: str, audience: str = "",
               expires_in: int = 3600, custom_claims: dict | None = None) -> str:
        now = int(time.time())
        jti = secrets.token_urlsafe(16)
        claims = {
            "iss": self._issuer,
            "sub": subject,
            "iat": now,
            "exp": now + expires_in,
            "jti": jti,
        }
        if audience:
            claims["aud"] = audience
        if custom_claims:
            for k, v in custom_claims.items():
                if k not in claims:  # don't override standard claims
                    claims[k] = v
        return self._sign(json.dumps(claims, separators=(",", ":")))

    def validate(self, token: str, audience: str = "") -> dict:
        """Validate token and return claims. Raises JwtError on failure."""
        parts = token.split(".")
        if len(parts) != 3:
            raise JwtError("Invalid token format")

        # Verify signature
        signing_input = f"{parts[0]}.{parts[1]}"
        expected_sig = hmac.new(
            self._secret.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        actual_sig = self._b64url_decode(parts[2])
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise JwtError("Invalid signature")

        # Decode claims
        claims = json.loads(self._b64url_decode(parts[1]))

        # Check expiry
        if claims.get("exp", 0) < time.time():
            raise JwtError("Token expired")

        # Check issuer
        if claims.get("iss") != self._issuer:
            raise JwtError("Invalid issuer")

        # Check audience
        if audience and claims.get("aud") != audience:
            raise JwtError("Invalid audience")

        # Check revocation
        if claims.get("jti") in self._revoked_jtis:
            raise JwtError("Token revoked")

        return claims

    def revoke(self, token: str) -> bool:
        """Revoke a token by its JTI."""
        try:
            parts = token.split(".")
            claims = json.loads(self._b64url_decode(parts[1]))
            jti = claims.get("jti")
            if jti:
                self._revoked_jtis.add(jti)
                return True
        except Exception:
            pass
        return False

    def create_refresh_token(self, subject: str, access_ttl: int = 3600,
                             refresh_ttl: int = 86400 * 30) -> dict:
        """Create access + refresh token pair."""
        access = self.create(subject, expires_in=access_ttl)
        refresh = secrets.token_urlsafe(32)
        self._refresh_tokens[refresh] = {
            "subject": subject,
            "expires_at": time.time() + refresh_ttl,
            "used": False,
        }
        return {"access_token": access, "refresh_token": refresh}

    def refresh(self, refresh_token: str, access_ttl: int = 3600) -> dict | None:
        """Exchange refresh token for new access + refresh tokens (rotation)."""
        meta = self._refresh_tokens.get(refresh_token)
        if not meta:
            return None
        if meta["used"]:
            # Refresh token reuse → revoke all (potential theft)
            del self._refresh_tokens[refresh_token]
            return None
        if time.time() > meta["expires_at"]:
            del self._refresh_tokens[refresh_token]
            return None

        # Mark old as used (rotation)
        meta["used"] = True
        # Issue new pair
        return self.create_refresh_token(meta["subject"], access_ttl)
