"""LTI Names and Role Provisioning Services v2 — membership pre-sync (R49).

The platform advertises a per-context membership endpoint in the launch
(namesroleservice claim, captured onto the resource link). An admin-triggered
sync fetches the course roster with a client_credentials token (NRPS scope)
and pushes every active member through identity resolution §9 — the same
link-first / verified-email / JIT / queue ladder as a live launch, so course
members have accounts BEFORE their first launch. No cohort writes: resource
links target skills/projects, not cohorts; placement stays a launch concern.

Trust: the membership document comes from the platform-registered URL over
TLS with a platform-issued token — the same trust root as launch claims, so
member emails carry the same email_verified treatment as launch emails.
"""

from __future__ import annotations

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import LtiRegistration, LtiResourceLink
from app.integrations.security import EgressClient, validate_egress_url
from app.integrations.services.identity import IdentityService, VerifiedExternalIdentity
from app.integrations.services.lti_ags import service_token

log = structlog.get_logger()

NRPS_SCOPE = "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
NRPS_CONTENT_TYPE = "application/vnd.ims.lti-nrps.v2.membershipcontainer+json"
_INSTRUCTOR_MARKER = "#Instructor"
_MAX_PAGES = 25


def _parse_next_link(link_header: str | None) -> str | None:
    """RFC 8288 Link header: the rel="next" target, if any."""
    for part in (link_header or "").split(","):
        seg = part.strip()
        if not seg.startswith("<") or ">" not in seg:
            continue
        url, _, params = seg.partition(">")
        if 'rel="next"' in params or "rel=next" in params:
            return url[1:]
    return None


async def sync_memberships(
    db: AsyncSession,
    org_id: str,
    link_id: str,
    *,
    egress: EgressClient | None = None,
) -> dict:
    link = await db.get(LtiResourceLink, link_id)
    reg = await db.get(LtiRegistration, link.registration_id) if link else None
    if link is None or reg is None or reg.org_id != org_id:
        raise AppError("LTI_RESOURCE_LINK_NOT_FOUND", "Resource link not found", 404)
    if reg.status != "active":
        raise AppError("LTI_REGISTRATION_INACTIVE", "Registration is not active", 409)
    if not link.nrps_url:
        raise AppError(
            "LTI_NRPS_UNAVAILABLE",
            "No membership endpoint — launch this link once so the platform "
            "advertises its NRPS URL",
            422,
        )

    egress = egress or EgressClient()
    token = await service_token(db, reg, egress, scope=NRPS_SCOPE)
    if token is None:
        raise AppError("LTI_NRPS_TOKEN_REFUSED", "Platform refused the NRPS token", 502)

    report = {"read": 0, "resolved": 0, "jit_created": 0, "queued": 0, "skipped": 0}
    identity = IdentityService(db)
    url: str | None = link.nrps_url
    pages = 0
    while url and pages < _MAX_PAGES:
        validate_egress_url(url)  # the next-link is platform data — screen it
        resp = await egress.request(
            "GET",
            url,
            headers={"authorization": f"Bearer {token}", "accept": NRPS_CONTENT_TYPE},
        )
        if resp.status_code == 401:
            raise AppError("LTI_NRPS_TOKEN_REFUSED", "Platform rejected the token", 502)
        if resp.status_code != 200:
            raise AppError("LTI_NRPS_FETCH_FAILED", f"NRPS {resp.status_code}", 502)
        try:
            doc = resp.json()
        except Exception as exc:
            raise AppError("LTI_NRPS_FETCH_FAILED", "NRPS body not JSON", 502) from exc
        # R476 (R471 class): a valid-JSON-but-non-object body (e.g. a top-level
        # array) would make doc.get(...) crash — reject it as a bad body.
        if not isinstance(doc, dict):
            raise AppError("LTI_NRPS_FETCH_FAILED", "NRPS body is not an object", 502)
        members = doc.get("members") or []
        if not isinstance(members, list):
            raise AppError("LTI_NRPS_FETCH_FAILED", "members is not a list", 502)
        for m in members:
            if not isinstance(m, dict):
                continue
            report["read"] += 1
            status = str(m.get("status") or "Active")
            sub = m.get("user_id")
            if status.lower() != "active" or not isinstance(sub, str) or not sub:
                report["skipped"] += 1
                continue
            roles = m.get("roles") or []
            is_instructor = any(isinstance(r, str) and _INSTRUCTOR_MARKER in r for r in roles)
            # Role ceiling: NRPS can mint at most instructor, never above the
            # registration's own JIT ceiling semantics.
            jit_role = "instructor" if is_instructor else reg.default_role
            ident = VerifiedExternalIdentity(
                org_id=reg.org_id,
                source="lti",
                connection_ref=reg.id,
                subject=f"{reg.issuer}|{sub}",
                email=m.get("email"),
                email_verified=bool(m.get("email")),
                display_name=m.get("name"),
            )
            try:
                result = await identity.resolve(ident, allow_jit=reg.allow_jit, jit_role=jit_role)
                report["resolved"] += 1
                report["jit_created"] += 1 if result.jit_created else 0
            except AppError as exc:
                if exc.code in ("IDENTITY_AMBIGUOUS", "SSO_NO_ACCOUNT"):
                    report["queued"] += 1  # row waits in the admin match queue
                elif exc.code == "SSO_JIT_ROLE_INVALID":
                    report["skipped"] += 1
                else:
                    raise
        url = _parse_next_link(resp.headers.get("link"))
        pages += 1
    return report
