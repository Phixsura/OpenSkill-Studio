"""SCIM 2.0 server logic (ADR-018 §5.3, RFC 7643/7644 narrow profile).

Deliberately hand-rolled payload handling: the production rules that matter
(lenient Entra PATCH parsing, soft-deprovision ≡ DELETE with session sweep,
delta group membership, reactivation-not-409) conflict with strict model
libraries, and our resource subset is tiny. Every rule here is pinned by a
test in tests/test_integrations_scim_db.py.

SCIM errors are SCIM-shaped (urn:...:Error), never the app envelope; no
payload echoes (PII) and no stack traces.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    GROUP_MAP_KINDS,
    MAX_SCIM_TOKENS_PER_ORG,
    SCIM_TOKEN_PREFIX,
    ExternalIdentityLink,
    ScimGroup,
    ScimGroupMember,
    ScimToken,
)
from app.models.organization import MemberStatus, OrgMember, OrgRole
from app.models.user import User, UserRole, UserStatus

log = structlog.get_logger()

SCIM_ERROR_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:Error"
SCIM_LIST_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:ListResponse"
SCIM_PATCH_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:PatchOp"
SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
SCIM_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"

# Role mapping ceiling — same rule as JIT (R88 class 4).
ROLE_MAP_ALLOWED = {"student": OrgRole.STUDENT, "instructor": OrgRole.INSTRUCTOR}


class ScimError(Exception):
    """Raised inside SCIM handlers; rendered as an RFC 7644 error body."""

    def __init__(self, status: int, detail: str, scim_type: str | None = None):
        self.status = status
        self.detail = detail
        self.scim_type = scim_type

    def body(self) -> dict:
        out: dict[str, Any] = {
            "schemas": [SCIM_ERROR_SCHEMA],
            "status": str(self.status),
            "detail": self.detail,
        }
        if self.scim_type:
            out["scimType"] = self.scim_type
        return out


# ── token admin (org-scoped surface) ──


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


class ScimTokenService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, org_id: str, *, name: str, group_map: dict | None, created_by: str
    ) -> tuple[ScimToken, str]:
        active = (
            await self.db.execute(
                select(ScimToken.id).where(
                    ScimToken.org_id == org_id, ScimToken.revoked_at.is_(None)
                )
            )
        ).all()
        if len(active) >= MAX_SCIM_TOKENS_PER_ORG:
            raise AppError("SCIM_TOKEN_LIMIT", "Too many active SCIM tokens", 422)
        self._validate_group_map(group_map or {})
        raw = f"{SCIM_TOKEN_PREFIX}{secrets.token_urlsafe(32)}"
        token = ScimToken(
            org_id=org_id,
            name=name,
            token_hash=hash_token(raw),
            group_map=group_map or {},
            created_by=created_by,
        )
        self.db.add(token)
        await self.db.flush()
        await self.db.refresh(token)
        return token, raw  # raw shown once, never retrievable

    @staticmethod
    def _validate_group_map(group_map: dict) -> None:
        for name, spec in group_map.items():
            if not isinstance(name, str) or not isinstance(spec, dict):
                raise AppError("SCIM_GROUP_MAP_INVALID", "group_map malformed", 422)
            kind = spec.get("kind")
            if kind not in GROUP_MAP_KINDS:
                raise AppError("SCIM_GROUP_MAP_INVALID", f"unknown kind for {name!r}", 422)
            if kind == "cohort" and not isinstance(spec.get("id"), str):
                raise AppError("SCIM_GROUP_MAP_INVALID", f"cohort id required for {name!r}", 422)
            if kind == "role" and spec.get("role") not in ROLE_MAP_ALLOWED:
                # Mint ceiling: owner/admin can never be group-mapped.
                raise AppError("SCIM_GROUP_MAP_INVALID", f"role not allowed for {name!r}", 422)

    async def list(self, org_id: str) -> list[ScimToken]:
        return list(
            (
                await self.db.execute(
                    select(ScimToken)
                    .where(ScimToken.org_id == org_id)
                    .order_by(ScimToken.created_at)
                )
            ).scalars()
        )

    async def update_group_map(self, org_id: str, token_id: str, group_map: dict) -> ScimToken:
        token = await self.db.get(ScimToken, token_id)
        if token is None or token.org_id != org_id:
            raise AppError("SCIM_TOKEN_NOT_FOUND", "Token not found", 404)
        self._validate_group_map(group_map)
        token.group_map = group_map
        await self.db.flush()
        return token

    async def revoke(self, org_id: str, token_id: str) -> None:
        token = await self.db.get(ScimToken, token_id)
        if token is None or token.org_id != org_id:
            raise AppError("SCIM_TOKEN_NOT_FOUND", "Token not found", 404)
        token.revoked_at = datetime.now(UTC)
        await self.db.flush()

    async def authenticate(self, raw: str) -> ScimToken:
        """Bearer -> token row; 401 shape handled by the router."""
        if not raw.startswith(SCIM_TOKEN_PREFIX):
            raise ScimError(401, "Invalid token")
        token = (
            await self.db.execute(
                select(ScimToken).where(
                    ScimToken.token_hash == hash_token(raw),
                    ScimToken.revoked_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if token is None:
            raise ScimError(401, "Invalid token")
        token.last_used_at = datetime.now(UTC)
        return token


# ── user resource logic ──


def _user_resource(user: User, member: OrgMember, link: ExternalIdentityLink | None) -> dict:
    return {
        "schemas": [SCIM_USER_SCHEMA],
        "id": user.id,
        "userName": user.email,
        "externalId": link.external_id if link else None,
        "displayName": user.display_name,
        "name": {"formatted": user.display_name},
        "emails": [{"value": user.email, "primary": True}],
        "active": member.status == MemberStatus.ACTIVE,
        "meta": {"resourceType": "User", "location": f"/api/v1/scim/v2/Users/{user.id}"},
    }


def _coerce_active(value: Any) -> bool | None:
    """Lenient deactivation parsing: Entra sends booleans, "False", "false",
    or wraps the value in a dict. None = not an active-flag payload."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "false"):
            return low == "true"
    if isinstance(value, dict) and "active" in value:
        return _coerce_active(value["active"])
    return None


def _normalize_path(path: str | None) -> str:
    """Strip fully-qualified attribute URNs; lowercase the attribute."""
    if not path:
        return ""
    p = path.strip()
    if p.lower().startswith(SCIM_USER_SCHEMA.lower() + ":"):
        p = p[len(SCIM_USER_SCHEMA) + 1 :]
    if p.lower().startswith(SCIM_GROUP_SCHEMA.lower() + ":"):
        p = p[len(SCIM_GROUP_SCHEMA) + 1 :]
    return p


class ScimUserService:
    def __init__(self, db: AsyncSession, token: ScimToken):
        self.db = db
        self.token = token
        self.org_id = token.org_id

    # — lookup helpers —

    async def _member_for(self, user_id: str) -> tuple[User, OrgMember]:
        user = await self.db.get(User, user_id)
        member = None
        if user is not None:
            member = (
                await self.db.execute(
                    select(OrgMember).where(
                        OrgMember.org_id == self.org_id, OrgMember.user_id == user_id
                    )
                )
            ).scalar_one_or_none()
        if user is None or member is None:
            # Cross-org ids are indistinguishable from unknown ids.
            raise ScimError(404, "Resource not found")
        return user, member

    async def _link_for(self, user_id: str) -> ExternalIdentityLink | None:
        return (
            await self.db.execute(
                select(ExternalIdentityLink).where(
                    ExternalIdentityLink.org_id == self.org_id,
                    ExternalIdentityLink.user_id == user_id,
                    ExternalIdentityLink.source == "scim",
                    ExternalIdentityLink.revoked_at.is_(None),
                )
            )
        ).scalar_one_or_none()

    async def get(self, user_id: str) -> dict:
        user, member = await self._member_for(user_id)
        return _user_resource(user, member, await self._link_for(user_id))

    # — list + filter —

    async def list(
        self, *, filter_expr: str | None, start_index: int, count: int
    ) -> dict:
        q = (
            select(User, OrgMember)
            .join(OrgMember, OrgMember.user_id == User.id)
            .where(OrgMember.org_id == self.org_id)
            .order_by(User.id)
        )
        if filter_expr:
            attr, value = self._parse_filter(filter_expr)
            if attr in ("username", "emails.value", "email"):
                q = q.where(func.lower(User.email) == value.lower())
            elif attr == "externalid":
                q = q.join(
                    ExternalIdentityLink,
                    (ExternalIdentityLink.user_id == User.id)
                    & (ExternalIdentityLink.org_id == self.org_id)
                    & (ExternalIdentityLink.source == "scim")
                    & (ExternalIdentityLink.revoked_at.is_(None)),
                ).where(ExternalIdentityLink.external_id == value)
            else:
                raise ScimError(400, f"Unsupported filter attribute: {attr}", "invalidFilter")
        rows = (await self.db.execute(q)).all()
        total = len(rows)
        page = rows[start_index - 1 : start_index - 1 + count]
        resources = []
        for user, member in page:
            resources.append(_user_resource(user, member, await self._link_for(user.id)))
        return {
            "schemas": [SCIM_LIST_SCHEMA],
            "totalResults": total,
            "startIndex": start_index,
            "itemsPerPage": len(resources),
            "Resources": resources,
        }

    @staticmethod
    def _parse_filter(expr: str) -> tuple[str, str]:
        """Supports exactly: <attr> eq "<value>" (v1 scope)."""
        import re

        m = re.fullmatch(r'\s*([A-Za-z.]+)\s+eq\s+"((?:[^"\\]|\\.)*)"\s*', expr)
        if not m:
            raise ScimError(400, "Only '<attr> eq \"value\"' filters are supported", "invalidFilter")
        return m.group(1).lower(), m.group(2)

    # — create (POST /Users) —

    async def create(self, payload: dict) -> tuple[dict, bool]:
        """Returns (resource, created). Reusing a soft-deleted userName
        REACTIVATES instead of 409 (draft-ansari rule)."""
        username = str(payload.get("userName", "")).strip().lower()
        if not username or "@" not in username or len(username) > 255:
            raise ScimError(400, "userName must be an email address", "invalidValue")
        display = str(
            payload.get("displayName")
            or (payload.get("name") or {}).get("formatted")
            or username.split("@", 1)[0]
        )[:100]
        active = _coerce_active(payload.get("active", True))
        external_id = payload.get("externalId")

        user = (
            await self.db.execute(select(User).where(func.lower(User.email) == username))
        ).scalar_one_or_none()
        if user is not None:
            member = (
                await self.db.execute(
                    select(OrgMember).where(
                        OrgMember.org_id == self.org_id, OrgMember.user_id == user.id
                    )
                )
            ).scalar_one_or_none()
            if member is not None and member.status == MemberStatus.ACTIVE:
                raise ScimError(409, "User already exists", "uniqueness")
            if member is not None:
                member.status = MemberStatus.ACTIVE  # reactivation, not 409
            else:
                member = OrgMember(
                    org_id=self.org_id,
                    user_id=user.id,
                    role=OrgRole.STUDENT,
                    status=MemberStatus.ACTIVE,
                )
                self.db.add(member)
        else:
            user = User(
                email=username,
                password_hash=None,
                display_name=display,
                role=UserRole.STUDENT,
                status=UserStatus.ACTIVE,
                email_verified=True,  # provisioned by the org's IdP
            )
            self.db.add(user)
            await self.db.flush()
            member = OrgMember(
                org_id=self.org_id,
                user_id=user.id,
                role=OrgRole.STUDENT,
                status=MemberStatus.ACTIVE,
            )
            self.db.add(member)
        await self.db.flush()
        await self._upsert_link(user.id, external_id)
        if active is False:
            await self._deprovision(user, member)
        await self._audit("org.scim.provisioned", user.id)
        return _user_resource(user, member, await self._link_for(user.id)), True

    async def _upsert_link(self, user_id: str, external_id) -> None:
        link = await self._link_for(user_id)
        if link is None:
            self.db.add(
                ExternalIdentityLink(
                    org_id=self.org_id,
                    user_id=user_id,
                    source="scim",
                    connection_ref=self.org_id,  # stable per-org namespace
                    subject=str(external_id or user_id),
                    external_id=str(external_id) if external_id is not None else None,
                )
            )
        elif external_id is not None:
            link.external_id = str(external_id)
        await self.db.flush()

    # — replace (PUT) —

    async def replace(self, user_id: str, payload: dict) -> dict:
        user, member = await self._member_for(user_id)
        display = payload.get("displayName") or (payload.get("name") or {}).get("formatted")
        if isinstance(display, str) and display.strip():
            user.display_name = display.strip()[:100]
        if payload.get("externalId") is not None:
            await self._upsert_link(user.id, payload["externalId"])
        active = _coerce_active(payload.get("active"))
        if active is False and member.status == MemberStatus.ACTIVE:
            await self._deprovision(user, member)
        elif active is True and member.status != MemberStatus.ACTIVE:
            member.status = MemberStatus.ACTIVE
        await self.db.flush()
        return _user_resource(user, member, await self._link_for(user_id))

    # — PATCH (lenient PatchOp) —

    async def patch(self, user_id: str, payload: dict) -> dict:
        user, member = await self._member_for(user_id)
        ops = payload.get("Operations")
        if not isinstance(ops, list) or not ops:
            raise ScimError(400, "Operations required", "invalidSyntax")
        # Validate EVERYTHING before applying ANYTHING (no partial apply).
        parsed: list[tuple[str, str, Any]] = []
        for op in ops:
            if not isinstance(op, dict):
                raise ScimError(400, "Invalid operation", "invalidSyntax")
            name = str(op.get("op", "")).strip().lower()  # case-insensitive
            if name not in ("add", "replace", "remove"):
                raise ScimError(400, f"Unsupported op: {name!r}", "invalidSyntax")
            parsed.append((name, _normalize_path(op.get("path")), op.get("value")))

        pending_active: bool | None = None
        for name, path, value in parsed:
            lowered = path.lower()
            if name in ("add", "replace"):
                if lowered == "active" or (not path and _coerce_active(value) is not None):
                    coerced = _coerce_active(value)
                    if coerced is None:
                        raise ScimError(400, "Invalid active value", "invalidValue")
                    pending_active = coerced
                elif lowered in ("displayname", "name.formatted"):
                    if isinstance(value, str) and value.strip():
                        user.display_name = value.strip()[:100]
                elif lowered == "externalid":
                    await self._upsert_link(user.id, value)
                # Unknown paths are stored-nothing no-ops (tolerant server).
            elif name == "remove" and lowered == "externalid":
                link = await self._link_for(user.id)
                if link is not None:
                    link.external_id = None
        if pending_active is False and member.status == MemberStatus.ACTIVE:
            await self._deprovision(user, member)
        elif pending_active is True and member.status != MemberStatus.ACTIVE:
            member.status = MemberStatus.ACTIVE
        await self.db.flush()
        return _user_resource(user, member, await self._link_for(user_id))

    # — delete ≡ deactivate —

    async def delete(self, user_id: str) -> None:
        user, member = await self._member_for(user_id)
        if member.status == MemberStatus.ACTIVE:
            await self._deprovision(user, member)

    async def _deprovision(self, user: User, member: OrgMember) -> None:
        """PATCH-deactivate ≡ DELETE: archive membership AND revoke sessions
        immediately (R88 revoke sweep incl. rotation predecessors). The user
        row is retained (soft delete; referential integrity + ≥90d window)."""
        member.status = MemberStatus.ARCHIVED
        from app.services.auth import AuthService

        await AuthService(self.db)._revoke_all_user_tokens(user.id)  # noqa: SLF001
        await self.db.flush()
        await self._audit("org.scim.deprovisioned", user.id)

    async def _audit(self, event: str, user_id: str) -> None:
        try:
            from app.integrations.facade import emit_event

            await emit_event(
                self.db,
                self.org_id,
                event,
                subject=user_id,
                data={"user_id": user_id, "token_id": self.token.id},
            )
        except Exception:
            log.warning("mesh_emit_failed", event=event, user_id=user_id)


# ── group resource logic ──


def _group_resource(group: ScimGroup, member_ids: list[str]) -> dict:
    return {
        "schemas": [SCIM_GROUP_SCHEMA],
        "id": group.id,
        "displayName": group.display_name,
        "externalId": group.external_id,
        "members": [{"value": uid} for uid in member_ids],
        "meta": {"resourceType": "Group", "location": f"/api/v1/scim/v2/Groups/{group.id}"},
    }


class ScimGroupService:
    def __init__(self, db: AsyncSession, token: ScimToken):
        self.db = db
        self.token = token
        self.org_id = token.org_id

    async def _group(self, group_id: str) -> ScimGroup:
        group = await self.db.get(ScimGroup, group_id)
        if group is None or group.org_id != self.org_id:
            raise ScimError(404, "Resource not found")
        return group

    async def _member_ids(self, group_id: str) -> list[str]:
        rows = await self.db.execute(
            select(ScimGroupMember.user_id).where(ScimGroupMember.group_id == group_id)
        )
        return [r for (r,) in rows.all()]

    async def get(self, group_id: str) -> dict:
        group = await self._group(group_id)
        return _group_resource(group, await self._member_ids(group.id))

    async def list(self, *, start_index: int, count: int) -> dict:
        groups = list(
            (
                await self.db.execute(
                    select(ScimGroup)
                    .where(ScimGroup.org_id == self.org_id)
                    .order_by(ScimGroup.id)
                )
            ).scalars()
        )
        total = len(groups)
        page = groups[start_index - 1 : start_index - 1 + count]
        resources = [_group_resource(g, await self._member_ids(g.id)) for g in page]
        return {
            "schemas": [SCIM_LIST_SCHEMA],
            "totalResults": total,
            "startIndex": start_index,
            "itemsPerPage": len(resources),
            "Resources": resources,
        }

    async def create(self, payload: dict) -> dict:
        name = str(payload.get("displayName", "")).strip()
        if not name or len(name) > 255:
            raise ScimError(400, "displayName required", "invalidValue")
        dup = (
            await self.db.execute(
                select(ScimGroup.id).where(
                    ScimGroup.org_id == self.org_id, ScimGroup.display_name == name
                )
            )
        ).scalar_one_or_none()
        if dup is not None:
            raise ScimError(409, "Group already exists", "uniqueness")
        group = ScimGroup(
            org_id=self.org_id,
            display_name=name,
            external_id=(
                str(payload["externalId"]) if payload.get("externalId") is not None else None
            ),
        )
        self.db.add(group)
        await self.db.flush()
        initial = payload.get("members") or []
        added = []
        for m in initial:
            uid = (m or {}).get("value")
            if isinstance(uid, str):
                added.append(uid)
        if added:
            await self._apply_member_delta(group, add=added, remove=[])
        return _group_resource(group, await self._member_ids(group.id))

    async def delete(self, group_id: str) -> None:
        group = await self._group(group_id)
        # Membership effects are NOT cascaded on group delete — removing the
        # mirror must not strip roles/cohorts the org may now manage manually.
        await self.db.delete(group)
        await self.db.flush()

    async def patch(self, group_id: str, payload: dict) -> dict:
        """Delta membership (never full-replace timeouts) + rename."""
        group = await self._group(group_id)
        ops = payload.get("Operations")
        if not isinstance(ops, list) or not ops:
            raise ScimError(400, "Operations required", "invalidSyntax")
        add: list[str] = []
        remove: list[str] = []
        rename: str | None = None
        import re

        for op in ops:
            if not isinstance(op, dict):
                raise ScimError(400, "Invalid operation", "invalidSyntax")
            name = str(op.get("op", "")).strip().lower()
            path = _normalize_path(op.get("path"))
            value = op.get("value")
            if name not in ("add", "replace", "remove"):
                raise ScimError(400, f"Unsupported op: {name!r}", "invalidSyntax")
            low = path.lower()
            if low == "displayname" and name in ("add", "replace"):
                if isinstance(value, str) and value.strip():
                    rename = value.strip()[:255]
                continue
            # members add/remove — plain path or filtered remove
            m = re.fullmatch(r'members\[value eq "([^"]+)"\]', path)
            if m and name == "remove":
                remove.append(m.group(1))
                continue
            if low == "members":
                vals = value if isinstance(value, list) else [value]
                ids = [
                    (v or {}).get("value")
                    for v in vals
                    if isinstance(v, dict) and isinstance(v.get("value"), str)
                ]
                if name in ("add",):
                    add.extend(ids)
                elif name == "remove":
                    remove.extend(ids)
                else:  # replace members = full set; compute the delta
                    current = set(await self._member_ids(group.id))
                    target = set(ids)
                    add.extend(target - current)
                    remove.extend(current - target)
        if rename:
            group.display_name = rename
        await self._apply_member_delta(group, add=add, remove=remove)
        return _group_resource(group, await self._member_ids(group.id))

    async def _apply_member_delta(
        self, group: ScimGroup, *, add: list[str], remove: list[str]
    ) -> None:
        """One transaction; each user validated to an org member; mapping
        effects (cohort/role) applied through the real services."""
        mapping = (self.token.group_map or {}).get(group.display_name)
        for uid in add:
            member = (
                await self.db.execute(
                    select(OrgMember).where(
                        OrgMember.org_id == self.org_id,
                        OrgMember.user_id == uid,
                        OrgMember.status == MemberStatus.ACTIVE,
                    )
                )
            ).scalar_one_or_none()
            if member is None:
                raise ScimError(400, "Member value is not a user in this organization", "invalidValue")
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            await self.db.execute(
                pg_insert(ScimGroupMember)
                .values(group_id=group.id, user_id=uid)
                .on_conflict_do_nothing(index_elements=["group_id", "user_id"])
            )
            await self._apply_mapping(mapping, member, joined=True)
        for uid in remove:
            row = (
                await self.db.execute(
                    select(ScimGroupMember).where(
                        ScimGroupMember.group_id == group.id, ScimGroupMember.user_id == uid
                    )
                )
            ).scalar_one_or_none()
            if row is None:
                continue  # idempotent remove
            await self.db.delete(row)
            member = (
                await self.db.execute(
                    select(OrgMember).where(
                        OrgMember.org_id == self.org_id, OrgMember.user_id == uid
                    )
                )
            ).scalar_one_or_none()
            if member is not None:
                await self._apply_mapping(mapping, member, joined=False)
        await self.db.flush()

    async def _apply_mapping(self, mapping, member: OrgMember, *, joined: bool) -> None:
        if not mapping:
            return  # unmapped groups are mirrored but have no effect
        if mapping.get("kind") == "role":
            role = ROLE_MAP_ALLOWED.get(mapping.get("role", ""))
            if role is None:
                return  # defensive: map validated at write, but re-check
            if joined:
                # Never demote an owner/admin via group sync.
                if member.role in (OrgRole.STUDENT, OrgRole.INSTRUCTOR):
                    member.role = role
            else:
                if member.role == role and role != OrgRole.STUDENT:
                    member.role = OrgRole.STUDENT
        elif mapping.get("kind") == "cohort":
            from app.models.cohort import CohortMember, CohortRole
            from app.services.cohort import CohortService

            cohort_id = mapping.get("id", "")
            if joined:
                try:
                    await CohortService(self.db).add_member(
                        cohort_id, member.user_id, CohortRole.LEARNER, self.org_id
                    )
                except AppError as exc:
                    # Already-member is fine; anything else surfaces.
                    if exc.code not in ("ALREADY_ENROLLED",):
                        log.warning(
                            "scim_cohort_map_failed", cohort_id=cohort_id, code=exc.code
                        )
            else:
                row = (
                    await self.db.execute(
                        select(CohortMember).where(
                            CohortMember.cohort_id == cohort_id,
                            CohortMember.user_id == member.user_id,
                        )
                    )
                ).scalar_one_or_none()
                if row is not None:
                    await self.db.delete(row)
