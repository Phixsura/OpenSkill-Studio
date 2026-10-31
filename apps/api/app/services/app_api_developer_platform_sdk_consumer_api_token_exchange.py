"""Consumer API Token Exchange — token exchange for cross-service authentication."""
from __future__ import annotations

import secrets
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

GRANT_TYPES = ("client_credentials", "authorization_code", "refresh_token", "token_exchange")


@dataclass
class ExchangeRequest:
    subject_token: str
    subject_token_type: str  # access_token, id_token, jwt
    target_audience: str
    scope: str = ""
    grant_type: str = "token_exchange"


@dataclass
class IssuedToken:
    token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = ""
    audience: str = ""
    issued_at: float = 0.0


@dataclass
class TokenExchange:
    """Exchange tokens for cross-service authentication."""

    _valid_tokens: dict[str, dict] = field(default_factory=dict)  # token -> metadata
    _issued: list[IssuedToken] = field(default_factory=list)
    _trusted_audiences: set[str] = field(default_factory=set)

    def register_token(self, token: str, consumer_id: str, scopes: list[str] | None = None,
                       token_type: str = "access_token") -> dict:
        self._valid_tokens[token] = {
            "consumer_id": consumer_id,
            "scopes": scopes or [],
            "token_type": token_type,
        }
        return {"registered": True, "token_prefix": token[:8]}

    def add_trusted_audience(self, audience: str) -> dict:
        self._trusted_audiences.add(audience)
        return {"audience": audience, "total": len(self._trusted_audiences)}

    def exchange(self, request: ExchangeRequest, current_time: float = 0.0) -> dict:
        if request.grant_type not in GRANT_TYPES:
            return {"error": "unsupported_grant_type"}
        # Validate subject token
        token_meta = self._valid_tokens.get(request.subject_token)
        if not token_meta:
            return {"error": "invalid_token", "description": "Subject token not recognized"}
        # Validate audience
        if self._trusted_audiences and request.target_audience not in self._trusted_audiences:
            return {"error": "invalid_target", "description": "Untrusted audience"}
        # Check scope
        requested_scopes = set(request.scope.split()) if request.scope else set()
        available_scopes = set(token_meta["scopes"])
        if requested_scopes and not requested_scopes.issubset(available_scopes):
            missing = requested_scopes - available_scopes
            return {"error": "insufficient_scope", "missing": sorted(missing)}
        # Issue new token
        new_token = secrets.token_hex(32)
        issued = IssuedToken(
            token=new_token, expires_in=3600,
            scope=request.scope or " ".join(token_meta["scopes"]),
            audience=request.target_audience, issued_at=current_time,
        )
        self._issued.append(issued)
        self._valid_tokens[new_token] = {
            "consumer_id": token_meta["consumer_id"],
            "scopes": token_meta["scopes"],
            "token_type": "access_token",
        }
        logger.info("token_exchanged", audience=request.target_audience)
        return {
            "access_token": new_token,
            "token_type": "Bearer",
            "expires_in": issued.expires_in,
            "scope": issued.scope,
            "audience": issued.audience,
        }

    def get_stats(self) -> dict:
        return {
            "registered_tokens": len(self._valid_tokens),
            "issued_exchanges": len(self._issued),
            "trusted_audiences": len(self._trusted_audiences),
        }
