"""OIDC relying party (ADR-018 §5.2) — the one SSO-shaped path.

Code flow implemented directly over EgressClient (every outbound fetch —
discovery, JWKS, token — rides the SSRF guard) + pyjwt for id_token
validation. SAML (P3b) will normalize into the same
VerifiedExternalIdentity struct; nothing downstream knows the protocol.

Validation set per launch (tests mirror this list):
  state: single-use DB row, 10-min TTL · nonce: must equal the state row's
  value (never a request param) · iss/aud exact · signature via JWKS with
  kid-miss single refetch rate-limited 30s/connection · exp/iat ±300s.
"""

from __future__ import annotations

import json
import secrets
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import jwt as pyjwt
import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt_credentials, encrypt_credentials
from app.exceptions import AppError
from app.integrations.models import SsoConnection, SsoLoginState
from app.integrations.security import EgressClient, validate_egress_url
from app.integrations.services.identity import (
    IdentityService,
    ResolutionResult,
    VerifiedExternalIdentity,
)

log = structlog.get_logger()

STATE_TTL = timedelta(minutes=10)
CLOCK_SKEW_S = 300
# kid-miss JWKS refetch floor per connection (S3.3/S1 research rule).
_JWKS_REFETCH_FLOOR_S = 30
# In-process JWKS cache: {connection_id: (fetched_monotonic, {kid: key})}
_jwks_cache: dict[str, tuple[float, dict]] = {}


def _invalid(reason: str) -> AppError:
    # One public error; the reason goes to logs only (no oracle).
    log.warning("sso_oidc_invalid", reason=reason)
    return AppError("SSO_ASSERTION_INVALID", "SSO response could not be validated", 401)


class OidcService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.egress = EgressClient()

    # ── connection config helpers ──

    async def _connection(self, sso_connection_id: str) -> SsoConnection:
        conn = await self.db.get(SsoConnection, sso_connection_id)
        if (
            conn is None
            or conn.protocol != "oidc"
            or conn.status not in ("testing", "active")
        ):
            raise AppError("SSO_CONNECTION_NOT_FOUND", "SSO connection not found", 404)
        return conn

    async def _discovery(self, conn: SsoConnection) -> dict:
        url = (conn.oidc_issuer or "").rstrip("/") + "/.well-known/openid-configuration"
        resp = await self.egress.request("GET", url)
        if resp.status_code != 200:
            raise _invalid("discovery_fetch_failed")
        try:
            doc = resp.json()
        except json.JSONDecodeError as exc:
            raise _invalid("discovery_not_json") from exc
        for key in ("authorization_endpoint", "token_endpoint", "jwks_uri", "issuer"):
            if not isinstance(doc.get(key), str):
                raise _invalid(f"discovery_missing_{key}")
            validate_egress_url(doc[key]) if key != "issuer" else None
        return doc

    # ── authorize (step 1) ──

    async def build_authorize_redirect(
        self, sso_connection_id: str, *, redirect_uri: str, return_to: str | None = None
    ) -> str:
        conn = await self._connection(sso_connection_id)
        doc = await self._discovery(conn)
        # Opportunistic purge (R7 defect #9): the unauthenticated authorize
        # endpoint mints a state row per hit — expired rows must not
        # accumulate forever. Cheap indexed delete, day-old grace.
        from sqlalchemy import delete as _delete

        await self.db.execute(
            _delete(SsoLoginState).where(
                SsoLoginState.expires_at < datetime.now(UTC) - timedelta(days=1)
            )
        )
        nonce = secrets.token_urlsafe(32)[:64]
        state = SsoLoginState(
            sso_connection_id=conn.id,
            nonce=nonce,
            redirect_to=return_to,
            expires_at=datetime.now(UTC) + STATE_TTL,
        )
        self.db.add(state)
        await self.db.flush()
        params = {
            "response_type": "code",
            "client_id": conn.oidc_client_id or "",
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "state": state.id,
            "nonce": nonce,
        }
        return f"{doc['authorization_endpoint']}?{urlencode(params)}"

    # ── callback (step 2) ──

    async def _consume_state(self, state_value: str) -> SsoLoginState:
        """Atomic single-use claim: UPDATE ... WHERE used_at IS NULL."""
        res = await self.db.execute(
            update(SsoLoginState)
            .where(
                SsoLoginState.id == state_value,
                SsoLoginState.used_at.is_(None),
                SsoLoginState.expires_at > datetime.now(UTC),
            )
            .values(used_at=datetime.now(UTC))
            .returning(SsoLoginState.id)
        )
        if res.scalar_one_or_none() is None:
            raise _invalid("state_unknown_used_or_expired")
        return (
            await self.db.execute(select(SsoLoginState).where(SsoLoginState.id == state_value))
        ).scalar_one()

    async def _jwks_keys(self, conn: SsoConnection, jwks_uri: str, *, kid: str) -> dict:
        now = time.monotonic()
        cached = _jwks_cache.get(conn.id)
        if cached is not None and kid in cached[1]:
            return cached[1]
        # kid miss (or no cache): refetch once, rate-limited per connection.
        if cached is not None and now - cached[0] < _JWKS_REFETCH_FLOOR_S:
            return cached[1]
        resp = await self.egress.request("GET", jwks_uri)
        if resp.status_code != 200:
            raise _invalid("jwks_fetch_failed")
        keys: dict[str, object] = {}
        try:
            for k in resp.json().get("keys", []):
                if k.get("kty") == "RSA" and k.get("kid"):
                    keys[k["kid"]] = pyjwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(k))
        except Exception as exc:
            raise _invalid("jwks_parse_failed") from exc
        _jwks_cache[conn.id] = (now, keys)
        return keys

    async def handle_callback(
        self, *, state_value: str, code: str, redirect_uri: str
    ) -> tuple[SsoConnection, ResolutionResult]:
        state = await self._consume_state(state_value)
        conn = await self._connection(state.sso_connection_id)
        doc = await self._discovery(conn)

        # Exchange the code (client_secret_post).
        secret = ""
        if conn.oidc_client_secret_ct:
            secret = decrypt_credentials(conn.oidc_client_secret_ct).get("client_secret", "")
        token_resp = await self.egress.request(
            "POST",
            doc["token_endpoint"],
            headers={"content-type": "application/x-www-form-urlencoded"},
            content=urlencode(
                {
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": conn.oidc_client_id or "",
                    "client_secret": secret,
                }
            ).encode(),
        )
        if token_resp.status_code != 200:
            raise _invalid("token_exchange_failed")
        try:
            id_token = token_resp.json().get("id_token", "")
        except json.JSONDecodeError as exc:
            raise _invalid("token_response_not_json") from exc
        if not id_token:
            raise _invalid("no_id_token")

        # Validate the id_token.
        try:
            header = pyjwt.get_unverified_header(id_token)
        except pyjwt.PyJWTError as exc:
            raise _invalid("jwt_header_invalid") from exc
        kid = header.get("kid", "")
        if header.get("alg") != "RS256":
            raise _invalid("alg_not_rs256")
        keys = await self._jwks_keys(conn, doc["jwks_uri"], kid=kid)
        key = keys.get(kid)
        if key is None:
            raise _invalid("kid_unknown")
        try:
            claims = pyjwt.decode(
                id_token,
                key=key,
                algorithms=["RS256"],
                audience=conn.oidc_client_id,
                issuer=doc["issuer"],
                leeway=CLOCK_SKEW_S,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except pyjwt.PyJWTError as exc:
            raise _invalid(f"jwt_invalid:{type(exc).__name__}") from exc
        # Nonce: session-stored value ONLY (a captured token reveals its own
        # nonce claim — never accept one echoed via request params).
        if claims.get("nonce") != state.nonce:
            raise _invalid("nonce_mismatch")

        amap = conn.attribute_map or {}
        email_claim = amap.get("email", "email")
        name_claim = amap.get("display_name", "name")
        ident = VerifiedExternalIdentity(
            org_id=conn.org_id,
            source="sso",
            connection_ref=conn.id,
            subject=str(claims["sub"]),
            email=claims.get(email_claim),
            email_verified=bool(claims.get("email_verified", False)),
            display_name=claims.get(name_claim),
        )
        result = await IdentityService(self.db).resolve(
            ident, allow_jit=conn.allow_jit, jit_role=conn.default_role
        )
        return conn, result


async def set_client_secret(conn: SsoConnection, secret: str) -> None:
    """Write-only client secret (same envelope as connection credentials)."""
    conn.oidc_client_secret_ct = encrypt_credentials({"client_secret": secret})
