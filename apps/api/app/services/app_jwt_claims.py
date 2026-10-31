"""App JWT Claims — validate and extract claims from JWT tokens.

Manages JWT claim validation for installed apps:
- Parse and extract claims
- Validate required claims
- Audience and issuer checks
- Expiry validation
"""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class ClaimValidationResult:
    """Result of validating JWT claims."""

    valid: bool
    claims: dict
    errors: list[str]


class AppJWTClaims:
    """Validate and extract claims from JWT tokens."""

    def __init__(
        self,
        required_claims: list[str] | None = None,
        expected_issuer: str = "",
        expected_audience: str = "",
    ) -> None:
        self._required = required_claims or []
        self._issuer = expected_issuer
        self._audience = expected_audience

    def extract_claims(self, token: str) -> dict:
        """Extract claims from a JWT (without signature verification)."""
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format: expected 3 parts")

        payload = parts[1]
        # Add padding
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        try:
            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)
        except Exception as e:
            raise ValueError(f"Failed to decode JWT payload: {e}") from e

    def validate(self, token: str, now: float | None = None) -> ClaimValidationResult:
        """Validate JWT claims."""
        now = now or time.time()
        errors: list[str] = []

        try:
            claims = self.extract_claims(token)
        except ValueError as e:
            return ClaimValidationResult(valid=False, claims={}, errors=[str(e)])

        # Required claims
        for claim in self._required:
            if claim not in claims:
                errors.append(f"Missing required claim: {claim}")

        # Issuer check
        if self._issuer and claims.get("iss") != self._issuer:
            errors.append(f"Invalid issuer: expected {self._issuer}")

        # Audience check
        if self._audience:
            aud = claims.get("aud")
            if isinstance(aud, list):
                if self._audience not in aud:
                    errors.append(f"Invalid audience: {self._audience} not in {aud}")
            elif aud != self._audience:
                errors.append(f"Invalid audience: expected {self._audience}")

        # Expiry check
        exp = claims.get("exp")
        if exp is not None and now >= exp:
            errors.append("Token expired")

        return ClaimValidationResult(
            valid=len(errors) == 0, claims=claims, errors=errors,
        )
