"""LTI Assignment & Grade Services — tool keys + score push (ADR-018 §8.2).

Grade return is explicit and per-link (grade_sync_enabled). The tool signs a
private_key_jwt client assertion with its own keypair (public half served at
/lti/jwks), exchanges it for an AGS-scoped token at the platform's token
endpoint, and POSTs a Score. Push failures log + emit an internal mesh event;
they never break the domain write that produced the grade (fail-safe).
"""

from __future__ import annotations

import json
import secrets
import time
from datetime import UTC, datetime

import jwt as pyjwt
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt_credentials, encrypt_credentials
from app.integrations.models import (
    ExternalIdentityLink,
    LtiRegistration,
    LtiResourceLink,
    LtiToolKey,
)
from app.integrations.security import EgressClient

log = structlog.get_logger()

AGS_SCORE_SCOPE = "https://purl.imsglobal.org/spec/lti-ags/scope/score"
SCORE_CONTENT_TYPE = "application/vnd.ims.lis.v1.score+json"


async def ensure_tool_key(db: AsyncSession) -> LtiToolKey:
    """Get-or-create the active tool signing keypair (one per environment)."""
    key = (
        await db.execute(select(LtiToolKey).where(LtiToolKey.active.is_(True)).limit(1))
    ).scalar_one_or_none()
    if key is not None:
        return key
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = rsa_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    kid = f"osks-{secrets.token_hex(8)}"
    jwk = json.loads(pyjwt.algorithms.RSAAlgorithm.to_jwk(rsa_key.public_key()))
    jwk.update({"kid": kid, "alg": "RS256", "use": "sig"})
    key = LtiToolKey(
        kid=kid,
        private_pem_ct=encrypt_credentials({"pem": pem}),
        public_jwk=jwk,
        active=True,
    )
    db.add(key)
    try:
        async with db.begin_nested():
            await db.flush()
    except Exception:
        # Concurrent first-use race: someone else created it — use theirs.
        existing = (
            await db.execute(
                select(LtiToolKey).where(LtiToolKey.active.is_(True)).limit(1)
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing
        raise
    return key


async def tool_jwks(db: AsyncSession) -> dict:
    keys = (
        await db.execute(select(LtiToolKey).where(LtiToolKey.active.is_(True)))
    ).scalars().all()
    return {"keys": [k.public_jwk for k in keys]}


async def _client_assertion(db: AsyncSession, reg: LtiRegistration) -> str:
    key = await ensure_tool_key(db)
    pem = decrypt_credentials(key.private_pem_ct)["pem"]
    now = int(time.time())
    return pyjwt.encode(
        {
            "iss": reg.client_id,
            "sub": reg.client_id,
            "aud": reg.auth_token_url,
            "jti": secrets.token_hex(16),
            "iat": now,
            "exp": now + 300,
        },
        pem,
        algorithm="RS256",
        headers={"kid": key.kid},
    )


async def _ags_token(db: AsyncSession, reg: LtiRegistration, egress: EgressClient) -> str | None:
    from urllib.parse import urlencode

    assertion = await _client_assertion(db, reg)
    resp = await egress.request(
        "POST",
        reg.auth_token_url,
        headers={"content-type": "application/x-www-form-urlencoded"},
        content=urlencode(
            {
                "grant_type": "client_credentials",
                "client_assertion_type": (
                    "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
                ),
                "client_assertion": assertion,
                "scope": AGS_SCORE_SCOPE,
            }
        ).encode(),
    )
    if resp.status_code != 200:
        log.warning("ags_token_refused", registration_id=reg.id, status=resp.status_code)
        return None
    return resp.json().get("access_token") or None


async def push_score(
    db: AsyncSession,
    link: LtiResourceLink,
    *,
    user_id: str,
    score_given: float,
    score_maximum: float = 100.0,
    egress: EgressClient | None = None,
) -> bool:
    """POST one AGS Score for a mapped launch user. Returns success."""
    if not link.grade_sync_enabled or not link.ags_lineitem_url:
        return False
    reg = await db.get(LtiRegistration, link.registration_id)
    if reg is None or reg.status != "active":
        return False
    # Our user -> LMS subject (the launch stored iss|sub as the link subject).
    subject = (
        await db.execute(
            select(ExternalIdentityLink.subject).where(
                ExternalIdentityLink.connection_ref == reg.id,
                ExternalIdentityLink.user_id == user_id,
                ExternalIdentityLink.revoked_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if subject is None:
        return False  # user never launched from this LMS — nothing to grade
    lms_user_id = subject.rsplit("|", 1)[-1]
    egress = egress or EgressClient()
    token = await _ags_token(db, reg, egress)
    if token is None:
        return False
    body = json.dumps(
        {
            "userId": lms_user_id,
            "scoreGiven": float(score_given),
            "scoreMaximum": float(score_maximum),
            "activityProgress": "Completed",
            "gradingProgress": "FullyGraded",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    ).encode()
    url = link.ags_lineitem_url.rstrip("/") + "/scores"
    resp = await egress.request(
        "POST", url, headers={"authorization": f"Bearer {token}", "content-type": SCORE_CONTENT_TYPE},
        content=body,
    )
    ok = 200 <= resp.status_code < 300
    if not ok:
        log.warning("ags_score_refused", link_id=link.id, status=resp.status_code)
    return ok


# ── deep linking (ADR §8 / LTI-DL 2.0) ──

DL_CLAIM = "https://purl.imsglobal.org/spec/lti-dl/claim/"
LTI_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/"


async def sign_deep_linking_response(
    db: AsyncSession,
    reg: LtiRegistration,
    *,
    deployment_id: str,
    content_items: list[dict],
    data: str | None = None,
) -> str:
    """Mint the signed LtiDeepLinkingResponse JWT the browser posts back to
    the platform's deep_link_return_url. Content items are tool-authored
    (ltiResourceLink entries pointing at our launch URL)."""
    key = await ensure_tool_key(db)
    pem = decrypt_credentials(key.private_pem_ct)["pem"]
    now = int(time.time())
    claims: dict = {
        "iss": reg.client_id,  # tool speaks as the client
        "aud": reg.issuer,
        "iat": now,
        "exp": now + 300,
        "nonce": secrets.token_hex(16),
        f"{LTI_CLAIM}message_type": "LtiDeepLinkingResponse",
        f"{LTI_CLAIM}version": "1.3.0",
        f"{LTI_CLAIM}deployment_id": deployment_id,
        f"{DL_CLAIM}content_items": content_items,
    }
    if data is not None:
        # Opaque platform state from the request MUST round-trip verbatim.
        claims[f"{DL_CLAIM}data"] = data
    return pyjwt.encode(claims, pem, algorithm="RS256", headers={"kid": key.kid})


def build_resource_link_item(*, title: str, launch_url: str, resource_id: str) -> dict:
    return {
        "type": "ltiResourceLink",
        "title": title[:200],
        "url": launch_url,
        "custom": {"resource_id": resource_id},
    }


# ── mesh-event hook (called fail-safe from the event fan-out handler) ──

GRADEABLE = {
    "com.openskill.project.approved.v1": ("project", "project_id", "final_score"),
    "com.openskill.skill.completed.v1": ("skill", "skill_id", None),
}


async def handle_gradeable_event(db: AsyncSession, event) -> int:
    """Push scores for every grade-enabled resource link mapped to the
    event's target in the event's org. Returns pushes attempted."""
    spec = GRADEABLE.get(event.type)
    if spec is None:
        return 0
    kind, target_key, score_key = spec
    data = event.data or {}
    target_id = str(data.get(target_key) or "")
    user_id = str(data.get("user_id") or "")
    if not target_id or not user_id:
        return 0
    links = (
        await db.execute(
            select(LtiResourceLink)
            .join(LtiRegistration, LtiRegistration.id == LtiResourceLink.registration_id)
            .where(
                LtiRegistration.org_id == event.org_id,
                LtiResourceLink.kind == kind,
                LtiResourceLink.target_id == target_id,
                LtiResourceLink.grade_sync_enabled.is_(True),
                LtiResourceLink.ags_lineitem_url.is_not(None),
            )
        )
    ).scalars().all()
    pushed = 0
    for link in links:
        score = 100.0
        if score_key is not None and data.get(score_key) is not None:
            try:
                score = max(0.0, min(100.0, float(data[score_key])))
            except (TypeError, ValueError):
                score = 0.0
        try:
            await push_score(db, link, user_id=user_id, score_given=score)
            pushed += 1
        except Exception as exc:  # never break the fan-out
            log.warning(
                "ags_push_failed",
                link_id=link.id,
                error=type(exc).__name__,
                detail=str(exc)[:200],
            )
    return pushed
