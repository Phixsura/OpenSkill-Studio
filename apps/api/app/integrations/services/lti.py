"""LTI 1.3 tool-side launch flow (ADR-018 §8.2).

Validation set on EVERY launch (each line is a test vector):
  state single-use + TTL · nonce equals the state row's value only ·
  iss matches registration · aud (and azp when present) equals client_id ·
  deployment_id in the registration's allowlist · RS256 signature via the
  platform JWKS (kid-miss: one refetch, 30s floor) · iat/exp ±300s ·
  version claim 1.3.0 · allowed message type.
"""

from __future__ import annotations

import json
import secrets
import time
from datetime import UTC, datetime, timedelta

import jwt as pyjwt
import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    JIT_ALLOWED_ROLES,
    LTI_MESSAGE_TYPES,
    LTI_RESOURCE_KINDS,
    LtiDeployment,
    LtiLaunchState,
    LtiRegistration,
    LtiResourceLink,
)
from app.integrations.security import EgressClient, validate_egress_url
from app.integrations.services.identity import (
    IdentityService,
    ResolutionResult,
    VerifiedExternalIdentity,
)

log = structlog.get_logger()

CLAIM = "https://purl.imsglobal.org/spec/lti/claim/"
STATE_TTL = timedelta(minutes=10)
CLOCK_SKEW_S = 300
_JWKS_REFETCH_FLOOR_S = 30
_jwks_cache: dict[str, tuple[float, dict]] = {}


def _invalid(reason: str) -> AppError:
    log.warning("lti_launch_invalid", reason=reason)
    return AppError("LTI_LAUNCH_INVALID", "LTI launch could not be validated", 401)


class LtiService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.egress = EgressClient()

    # ── admin ──

    async def create_registration(
        self,
        org_id: str,
        *,
        issuer: str,
        client_id: str,
        auth_login_url: str,
        auth_token_url: str,
        jwks_url: str,
        deployment_ids: list[str],
        allow_jit: bool = True,
        default_role: str = "student",
    ) -> LtiRegistration:
        for url in (issuer, auth_login_url, auth_token_url, jwks_url):
            validate_egress_url(url)
        if default_role not in JIT_ALLOWED_ROLES:
            raise AppError("SSO_JIT_ROLE_INVALID", "default_role not allowed", 422)
        reg = LtiRegistration(
            org_id=org_id,
            issuer=issuer.rstrip("/"),
            client_id=client_id,
            auth_login_url=auth_login_url,
            auth_token_url=auth_token_url,
            jwks_url=jwks_url,
            allow_jit=allow_jit,
            default_role=default_role,
        )
        try:
            # SAVEPOINT so the duplicate-key rollback fully expunges the
            # pending row instead of poisoning the caller's session (R422).
            async with self.db.begin_nested():
                self.db.add(reg)
                await self.db.flush()
        except Exception as exc:
            raise AppError("LTI_REGISTRATION_EXISTS", "issuer+client already registered", 409) from exc
        for dep in deployment_ids:
            if isinstance(dep, str) and dep:
                self.db.add(LtiDeployment(registration_id=reg.id, deployment_id=dep[:255]))
        await self.db.flush()
        await self.db.refresh(reg)
        return reg

    async def get_registration(self, org_id: str, reg_id: str) -> LtiRegistration:
        reg = await self.db.get(LtiRegistration, reg_id)
        if reg is None or reg.org_id != org_id:
            raise AppError("LTI_REGISTRATION_NOT_FOUND", "Registration not found", 404)
        return reg

    async def map_resource_link(
        self,
        org_id: str,
        reg_id: str,
        *,
        deployment_id: str,
        resource_link_id: str,
        kind: str,
        target_id: str,
        grade_sync_enabled: bool = False,
    ) -> LtiResourceLink:
        await self.get_registration(org_id, reg_id)
        if kind not in LTI_RESOURCE_KINDS:
            raise AppError("LTI_RESOURCE_KIND_INVALID", "bad kind", 422)
        existing = (
            await self.db.execute(
                select(LtiResourceLink).where(
                    LtiResourceLink.registration_id == reg_id,
                    LtiResourceLink.deployment_id == deployment_id,
                    LtiResourceLink.resource_link_id == resource_link_id,
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            existing.kind = kind
            existing.target_id = target_id
            existing.grade_sync_enabled = grade_sync_enabled
            await self.db.flush()
            return existing
        link = LtiResourceLink(
            registration_id=reg_id,
            deployment_id=deployment_id,
            resource_link_id=resource_link_id,
            kind=kind,
            target_id=target_id,
            grade_sync_enabled=grade_sync_enabled,
        )
        self.db.add(link)
        await self.db.flush()
        return link

    # ── login initiation (step 1) ──

    async def login_initiation(
        self, *, iss: str, login_hint: str, client_id: str | None, lti_message_hint: str | None,
        target_link_uri: str, redirect_uri: str,
    ) -> str:
        q = select(LtiRegistration).where(
            LtiRegistration.issuer == iss.rstrip("/"), LtiRegistration.status == "active"
        )
        if client_id:
            q = q.where(LtiRegistration.client_id == client_id)
        reg = (await self.db.execute(q)).scalars().first()
        if reg is None:
            raise _invalid("unknown_issuer")
        # Opportunistic purge of expired launch states (R7 defect #9).
        from sqlalchemy import delete as _delete

        await self.db.execute(
            _delete(LtiLaunchState).where(
                LtiLaunchState.expires_at < datetime.now(UTC) - timedelta(days=1)
            )
        )
        state = LtiLaunchState(
            registration_id=reg.id,
            nonce=secrets.token_urlsafe(32)[:64],
            expires_at=datetime.now(UTC) + STATE_TTL,
        )
        self.db.add(state)
        await self.db.flush()
        from urllib.parse import urlencode

        params = {
            "response_type": "id_token",
            "response_mode": "form_post",
            "scope": "openid",
            "prompt": "none",
            "client_id": reg.client_id,
            "redirect_uri": redirect_uri,
            "state": state.id,
            "nonce": state.nonce,
            "login_hint": login_hint,
        }
        if lti_message_hint:
            params["lti_message_hint"] = lti_message_hint
        return f"{reg.auth_login_url}?{urlencode(params)}"

    # ── launch (step 2) ──

    async def _consume_state(self, state_value: str) -> LtiLaunchState:
        res = await self.db.execute(
            update(LtiLaunchState)
            .where(
                LtiLaunchState.id == state_value,
                LtiLaunchState.used_at.is_(None),
                LtiLaunchState.expires_at > datetime.now(UTC),
            )
            .values(used_at=datetime.now(UTC))
            .returning(LtiLaunchState.id)
        )
        if res.scalar_one_or_none() is None:
            raise _invalid("state_unknown_used_or_expired")
        return (
            await self.db.execute(
                select(LtiLaunchState).where(LtiLaunchState.id == state_value)
            )
        ).scalar_one()

    async def _jwks_keys(self, reg: LtiRegistration, *, kid: str) -> dict:
        now = time.monotonic()
        cached = _jwks_cache.get(reg.id)
        if cached is not None and kid in cached[1]:
            return cached[1]
        if cached is not None and now - cached[0] < _JWKS_REFETCH_FLOOR_S:
            return cached[1]
        resp = await self.egress.request("GET", reg.jwks_url)
        if resp.status_code != 200:
            raise _invalid("jwks_fetch_failed")
        keys: dict[str, object] = {}
        try:
            for k in resp.json().get("keys", []):
                if k.get("kty") == "RSA" and k.get("kid"):
                    keys[k["kid"]] = pyjwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(k))
        except Exception as exc:
            raise _invalid("jwks_parse_failed") from exc
        _jwks_cache[reg.id] = (now, keys)
        return keys

    async def handle_launch(
        self, *, state_value: str, id_token: str
    ) -> tuple[LtiRegistration, LtiResourceLink | None, ResolutionResult, dict]:
        state = await self._consume_state(state_value)
        reg = await self.db.get(LtiRegistration, state.registration_id)
        if reg is None or reg.status != "active":
            raise _invalid("registration_inactive")

        try:
            header = pyjwt.get_unverified_header(id_token)
        except pyjwt.PyJWTError as exc:
            raise _invalid("jwt_header_invalid") from exc
        if header.get("alg") != "RS256":
            raise _invalid("alg_not_rs256")
        keys = await self._jwks_keys(reg, kid=header.get("kid", ""))
        key = keys.get(header.get("kid", ""))
        if key is None:
            raise _invalid("kid_unknown")
        try:
            claims = pyjwt.decode(
                id_token,
                key=key,
                algorithms=["RS256"],
                audience=reg.client_id,
                issuer=reg.issuer,
                leeway=CLOCK_SKEW_S,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except pyjwt.PyJWTError as exc:
            raise _invalid(f"jwt_invalid:{type(exc).__name__}") from exc
        # azp, when present, must be our client id (multi-audience tokens).
        if claims.get("azp") and claims["azp"] != reg.client_id:
            raise _invalid("azp_mismatch")
        # Nonce: session-stored value ONLY (a captured token reveals its own
        # nonce claim — never accept one echoed via request params).
        if claims.get("nonce") != state.nonce:
            raise _invalid("nonce_mismatch")
        if claims.get(f"{CLAIM}version") != "1.3.0":
            raise _invalid("version_not_1_3")
        message_type = claims.get(f"{CLAIM}message_type", "")
        if message_type not in LTI_MESSAGE_TYPES:
            raise _invalid("message_type_not_allowed")
        deployment_id = str(claims.get(f"{CLAIM}deployment_id", ""))
        allowed = (
            await self.db.execute(
                select(LtiDeployment.id).where(
                    LtiDeployment.registration_id == reg.id,
                    LtiDeployment.deployment_id == deployment_id,
                )
            )
        ).scalar_one_or_none()
        if allowed is None:
            # Deployment allowlist (string compare — §8.1): unlisted launches
            # are rejected, with their own machine code for admin triage.
            raise AppError("LTI_DEPLOYMENT_UNKNOWN", "Deployment not registered", 401)

        # Identity: stable subject = iss|sub (sub alone is per-issuer).
        email = claims.get("email")
        ident = VerifiedExternalIdentity(
            org_id=reg.org_id,
            source="lti",
            connection_ref=reg.id,
            subject=f"{reg.issuer}|{claims['sub']}",
            email=email,
            # LMS launches carry platform-asserted identity; email (when
            # present) is as trustworthy as the platform itself — same trust
            # root as the registration the admin configured.
            email_verified=bool(email),
            display_name=claims.get("name"),
        )
        result = await IdentityService(self.db).resolve(
            ident, allow_jit=reg.allow_jit, jit_role=reg.default_role
        )

        # Resource link mapping (None for deep-linking requests or unmapped
        # placements — the caller decides what to render).
        link = None
        rl = claims.get(f"{CLAIM}resource_link") or {}
        if message_type == "LtiResourceLinkRequest" and rl.get("id"):
            link = (
                await self.db.execute(
                    select(LtiResourceLink).where(
                        LtiResourceLink.registration_id == reg.id,
                        LtiResourceLink.deployment_id == deployment_id,
                        LtiResourceLink.resource_link_id == str(rl["id"]),
                    )
                )
            ).scalar_one_or_none()
            # AGS endpoint claim: remember the lineitem URL for grade push.
            ags = claims.get(f"{CLAIM.replace('lti/claim/', 'lti-ags/claim/')}endpoint") or {}
            if link is not None and isinstance(ags, dict) and ags.get("lineitem"):
                lineitem = str(ags["lineitem"])[:500]
                try:
                    validate_egress_url(lineitem)
                    link.ags_lineitem_url = lineitem
                except AppError:
                    log.warning("lti_ags_lineitem_blocked", url=lineitem[:100])

        return reg, link, result, claims
