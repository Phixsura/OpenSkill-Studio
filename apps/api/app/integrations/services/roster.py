"""Roster provisioning: staged canonical roster -> Cohort/CohortMember
(ADR-018 §6.2).

Provisioning is a SEPARATE explicit pass over staged records — external data
never writes production tables during sync. Conflicted records are skipped,
never guessed (admin resolves; the next pass applies). All writes go through
the same service functions the UI uses (CohortService), so max_learners,
frozen-cohort and membership rules hold for SIS data too.

Deviation from the ADR's `archive_membership` wording (§6.2): CohortMember
has no archived state in the product model — the unenroll policy is
`remove_membership` (default) or `ignore`.
"""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    ExternalIdentityLink,
    IntegrationConnection,
    StagedRecord,
    SyncRecordResult,
    SyncRun,
)
from app.integrations.services.identity import IdentityService, VerifiedExternalIdentity
from app.models.cohort import Cohort, CohortMember, CohortRole
from app.services.cohort import AlreadyCohortMemberError, CohortService

log = structlog.get_logger()

UNENROLL_POLICIES = frozenset({"remove_membership", "ignore"})

ROSTER_ROLE_MAP = {
    "student": CohortRole.LEARNER,
    "teacher": CohortRole.INSTRUCTOR,
    "instructor": CohortRole.INSTRUCTOR,
}


class RosterProvisioningService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def provision(
        self,
        org_id: str,
        connection_id: str,
        *,
        actor_id: str,
        options: dict | None = None,
    ) -> dict:
        """One provisioning pass. Returns a report; conflict rows attach to
        the connection's most recent roster sync run (observability surface
        shared with the engine, §11.4)."""
        conn = await self.db.get(IntegrationConnection, connection_id)
        if conn is None or conn.org_id != org_id:
            raise AppError("CONNECTION_NOT_FOUND", "Connection not found", 404)
        opts = options or {}
        auto_create = bool(opts.get("auto_create_cohorts", True))
        jit_users = bool(opts.get("jit_users", False))
        on_unenroll = opts.get("on_unenroll", "remove_membership")
        if on_unenroll not in UNENROLL_POLICIES:
            raise AppError("ROSTER_OPTIONS_INVALID", "bad on_unenroll policy", 422)

        run_id = await self._latest_run_id(connection_id)

        report: dict = {
            "cohorts_created": 0,
            "members_added": 0,
            "members_removed": 0,
            "unchanged": 0,
            "conflicts": 0,
        }

        cohort_by_class = await self._provision_classes(
            org_id, connection_id, actor_id, auto_create, run_id, report
        )
        await self._provision_enrollments(
            org_id, connection_id, cohort_by_class, jit_users, on_unenroll, run_id, report
        )
        await self.db.flush()
        return report

    async def _latest_run_id(self, connection_id: str) -> str | None:
        from app.integrations.models import SyncProfile

        return (
            await self.db.execute(
                select(SyncRun.id)
                .join(SyncProfile, SyncProfile.id == SyncRun.profile_id)
                .where(
                    SyncProfile.connection_id == connection_id,
                    SyncProfile.model.in_(("roster.class", "roster.enrollment")),
                )
                .order_by(SyncRun.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

    def _conflict(
        self,
        run_id: str | None,
        external_id: str,
        model: str,
        conflict_class: str,
        detail: dict,
        report: dict,
    ) -> None:
        report["conflicts"] += 1
        if run_id is not None:
            self.db.add(
                SyncRecordResult(
                    run_id=run_id,
                    external_id=external_id,
                    model=model,
                    outcome="conflict",
                    conflict_class=conflict_class,
                    detail=detail,
                )
            )

    # ── classes -> cohorts ──

    async def _provision_classes(
        self,
        org_id: str,
        connection_id: str,
        actor_id: str,
        auto_create: bool,
        run_id: str | None,
        report: dict,
    ) -> dict[str, str]:
        staged = (
            await self.db.execute(
                select(StagedRecord).where(
                    StagedRecord.connection_id == connection_id,
                    StagedRecord.model == "roster.class",
                    StagedRecord.status == "active",
                )
            )
        ).scalars().all()
        # Existing provisioned cohorts: settings.integration backlink.
        cohorts = (
            await self.db.execute(select(Cohort).where(Cohort.org_id == org_id))
        ).scalars().all()
        by_external: dict[str, Cohort] = {}
        for c in cohorts:
            integ = (c.settings or {}).get("integration") or {}
            if integ.get("connection_id") == connection_id and integ.get("external_id"):
                by_external[integ["external_id"]] = c

        svc = CohortService(self.db)
        out: dict[str, str] = {}
        for rec in staged:
            title = str((rec.payload or {}).get("title") or "").strip()
            if not title:
                self._conflict(
                    run_id, rec.external_id, "roster.class", "schema_invalid",
                    {"missing": "title"}, report,
                )
                continue
            cohort = by_external.get(rec.external_id)
            if cohort is None:
                if not auto_create:
                    self._conflict(
                        run_id, rec.external_id, "roster.class", "missing_reference",
                        {"reason": "no_cohort_and_auto_create_off"}, report,
                    )
                    continue
                cohort = await svc.create_cohort(
                    org_id=org_id,
                    name=title[:200],
                    description=None,
                    created_by=actor_id,
                )
                settings = dict(cohort.settings or {})
                settings["integration"] = {
                    "connection_id": connection_id,
                    "external_id": rec.external_id,
                }
                cohort.settings = settings
                by_external[rec.external_id] = cohort
                report["cohorts_created"] += 1
            else:
                report["unchanged"] += 1
            out[rec.external_id] = cohort.id
        return out

    # ── enrollments -> cohort members ──

    async def _provision_enrollments(
        self,
        org_id: str,
        connection_id: str,
        cohort_by_class: dict[str, str],
        jit_users: bool,
        on_unenroll: str,
        run_id: str | None,
        report: dict,
    ) -> None:
        staged = (
            await self.db.execute(
                select(StagedRecord).where(
                    StagedRecord.connection_id == connection_id,
                    StagedRecord.model == "roster.enrollment",
                )
            )
        ).scalars().all()
        svc = CohortService(self.db)
        for rec in staged:
            p = rec.payload or {}
            class_ext = str(p.get("class_external_id") or "")
            user_ext = str(p.get("user_external_id") or "")
            role_raw = str(p.get("role") or "student").lower()
            cohort_id = cohort_by_class.get(class_ext)
            if rec.status == "active":
                if cohort_id is None:
                    self._conflict(
                        run_id, rec.external_id, "roster.enrollment", "missing_reference",
                        {"class_external_id": class_ext}, report,
                    )
                    continue
                role = ROSTER_ROLE_MAP.get(role_raw)
                if role is None:
                    self._conflict(
                        run_id, rec.external_id, "roster.enrollment", "role_conflict",
                        {"role": role_raw}, report,
                    )
                    continue
                user_id = await self._resolve_user(
                    org_id, connection_id, user_ext, jit_users, run_id, rec, report
                )
                if user_id is None:
                    continue
                existing = (
                    await self.db.execute(
                        select(CohortMember).where(
                            CohortMember.cohort_id == cohort_id,
                            CohortMember.user_id == user_id,
                        )
                    )
                ).scalar_one_or_none()
                if existing is not None:
                    if existing.role != role:
                        # Manual role differs from SIS: a human decided —
                        # report, never overwrite (§6.2 rule 4).
                        self._conflict(
                            run_id, rec.external_id, "roster.enrollment", "role_conflict",
                            {"local": existing.role.value, "external": role.value}, report,
                        )
                    else:
                        report["unchanged"] += 1
                    continue
                try:
                    await svc.add_member(cohort_id, user_id, role, org_id)
                    report["members_added"] += 1
                except AlreadyCohortMemberError:
                    report["unchanged"] += 1
                except AppError as exc:
                    self._conflict(
                        run_id, rec.external_id, "roster.enrollment", "schema_invalid",
                        {"code": exc.code}, report,
                    )
            elif rec.status == "tombstoned" and on_unenroll == "remove_membership":
                if cohort_id is None:
                    continue
                link_user = await self._linked_user(connection_id, user_ext)
                if link_user is None:
                    continue
                existing = (
                    await self.db.execute(
                        select(CohortMember).where(
                            CohortMember.cohort_id == cohort_id,
                            CohortMember.user_id == link_user,
                        )
                    )
                ).scalar_one_or_none()
                if existing is not None:
                    await self.db.delete(existing)
                    report["members_removed"] += 1

    async def _linked_user(self, connection_id: str, user_ext: str) -> str | None:
        return (
            await self.db.execute(
                select(ExternalIdentityLink.user_id).where(
                    ExternalIdentityLink.connection_ref == connection_id,
                    ExternalIdentityLink.subject == user_ext,
                    ExternalIdentityLink.revoked_at.is_(None),
                )
            )
        ).scalar_one_or_none()

    async def _resolve_user(
        self,
        org_id: str,
        connection_id: str,
        user_ext: str,
        jit_users: bool,
        run_id: str | None,
        rec: StagedRecord,
        report: dict,
    ) -> str | None:
        if not user_ext:
            self._conflict(
                run_id, rec.external_id, "roster.enrollment", "schema_invalid",
                {"missing": "user_external_id"}, report,
            )
            return None
        linked = await self._linked_user(connection_id, user_ext)
        if linked is not None:
            return linked
        # Try the staged roster.user record for an email to resolve with.
        user_rec = (
            await self.db.execute(
                select(StagedRecord).where(
                    StagedRecord.connection_id == connection_id,
                    StagedRecord.model == "roster.user",
                    StagedRecord.external_id == user_ext,
                    StagedRecord.status == "active",
                )
            )
        ).scalar_one_or_none()
        email = str(((user_rec.payload if user_rec else {}) or {}).get("email") or "").lower()
        if not email:
            self._conflict(
                run_id, rec.external_id, "roster.enrollment", "ambiguous_identity",
                {"user_external_id": user_ext, "reason": "no_email"}, report,
            )
            return None
        ident = VerifiedExternalIdentity(
            org_id=org_id,
            source="roster",
            connection_ref=connection_id,
            subject=user_ext,
            email=email,
            # SIS data arrives over the org's authenticated connection — the
            # org vouches for it the way an IdP does (same trust root as SCIM).
            email_verified=True,
            display_name=str((user_rec.payload or {}).get("display_name") or "") or None,
        )
        try:
            result = await IdentityService(self.db).resolve(
                ident, allow_jit=jit_users, jit_role="student"
            )
        except AppError:
            # Queued for admin confirmation — skip, never guess (§6.2).
            self._conflict(
                run_id, rec.external_id, "roster.enrollment", "ambiguous_identity",
                {"user_external_id": user_ext}, report,
            )
            return None
        return result.user.id
