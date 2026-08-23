"""Workflow Pack service — CRUD, definition management, immutable releases (ADR-010).

Mirrors skill_pack.py distribution semantics. Definitions are validated
against the closed step vocabulary on every write; releases snapshot the
definition immutably with a sha256 checksum.
"""

import hashlib
import json
import re
import secrets
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.skill_pack import PackStatus, PackVisibility
from app.models.workflow_pack import WorkflowPack, WorkflowPackRelease
from app.schemas.workflow_definition import (
    derive_io_schemas,
    validate_definition,
    validate_or_raise,
)

log = structlog.get_logger()

# Version constraint grammar v1: exact X.Y.Z or >=X.Y.Z only (R7 anti-over-pinning)
_VERSION_CONSTRAINT_RE = re.compile(r"^(>=)?\d+\.\d+\.\d+$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")

MAX_DEPENDENCIES = 20


def _parse_semver(version: str) -> tuple[int, int, int, str]:
    """Parse 'X.Y.Z' or 'X.Y.Z-prerelease' into a comparable tuple."""
    base, _, prerelease = version.partition("-")
    parts = base.split(".")
    pre_key = prerelease if prerelease else "~"  # '~' > all ASCII letters
    return (int(parts[0]), int(parts[1]), int(parts[2]), pre_key)


class WorkflowPackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD ──────────────────────────────────────────────

    async def create_pack(self, org_id: str, created_by: str, **fields) -> WorkflowPack:
        name = fields.pop("name")
        slug = f"{self._generate_slug(name)[:190]}-{secrets.token_hex(3)}"
        pack = WorkflowPack(
            owner_org_id=org_id,
            name=name,
            slug=slug,
            created_by=created_by,
            **fields,
        )
        self.db.add(pack)
        await self.db.flush()
        log.info("workflow_pack_created", pack_id=pack.id, org_id=org_id)
        return pack

    async def list_packs(
        self, org_id: str, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[WorkflowPack], int]:
        query = select(WorkflowPack).where(WorkflowPack.owner_org_id == org_id)
        if status:
            query = query.where(WorkflowPack.status == PackStatus(status))
        else:
            query = query.where(WorkflowPack.status != PackStatus.ARCHIVED)
        total_r = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = total_r.scalar_one()
        result = await self.db.execute(
            query.order_by(WorkflowPack.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_pack(self, pack_id: str, org_id: str) -> WorkflowPack:
        pack = await self.db.get(WorkflowPack, pack_id)
        if pack is None or pack.owner_org_id != org_id or pack.status == PackStatus.ARCHIVED:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)
        return pack

    async def update_pack(self, pack_id: str, org_id: str, **fields) -> WorkflowPack:
        pack = await self.get_pack(pack_id, org_id)
        # Approval gate: public visibility is only reachable through the
        # review flow (submit-review → approve). Direct PUT visibility=public
        # on an unapproved pack would bypass the registry approval filter
        # (which accepts review_status IS NULL).
        requested_visibility = fields.get("visibility")
        if (
            requested_visibility in ("public", PackVisibility.PUBLIC)
            and pack.review_status != "approved"
        ):
            raise AppError(
                "APPROVAL_REQUIRED",
                "Public visibility requires approval — submit for review first",
                422,
            )
        if "name" in fields and fields["name"] and fields["name"] != pack.name:
            pack.slug = f"{self._generate_slug(fields['name'])[:190]}-{secrets.token_hex(3)}"
        for key, value in fields.items():
            if value is not None and hasattr(pack, key):
                setattr(pack, key, value)
        try:
            await self.db.flush()
        except IntegrityError:
            raise AppError("SLUG_CONFLICT", "A pack with this name already exists", 409) from None
        await self.db.refresh(pack)
        await self._invalidate_registry_cache()
        return pack

    async def delete_pack(self, pack_id: str, org_id: str) -> None:
        pack = await self.get_pack(pack_id, org_id)
        pack.status = PackStatus.ARCHIVED
        await self.db.flush()
        await self._invalidate_registry_cache()
        log.info("workflow_pack_archived", pack_id=pack_id, org_id=org_id)

    # ── Definition ────────────────────────────────────────

    async def update_definition(self, pack_id: str, org_id: str, definition: dict) -> WorkflowPack:
        """Update the working definition. Draft-editable only; releases are immutable."""
        pack = await self.get_pack(pack_id, org_id)
        parsed = validate_or_raise(definition)
        pack.definition = definition
        inputs, outputs = derive_io_schemas(parsed)
        pack.input_schema = inputs
        pack.output_schema = outputs
        # Derive capability tags from provider_action steps for registry search
        caps = sorted(
            {
                s.config.get("capability", "")
                for s in parsed.steps
                if s.type == "provider_action" and s.config.get("capability")
            }
        )
        pack.capability_tags = caps
        pack.definition_updated_at = datetime.now(UTC)
        # A definition change mutates registry-facing fields (input/output
        # schemas, capability tags). An approved-public pack must re-enter
        # review so the public card can never drift from what was approved.
        if pack.review_status == "approved" and pack.visibility == PackVisibility.PUBLIC:
            pack.review_status = None
            pack.visibility = PackVisibility.UNLISTED
            log.info(
                "workflow_pack_approval_reset_on_definition_change",
                pack_id=pack_id,
                org_id=org_id,
            )
        await self.db.flush()
        await self.db.refresh(pack)
        await self._invalidate_registry_cache()
        return pack

    async def validate_pack_definition(self, definition: dict) -> list[dict]:
        """Dry-run validation — returns error list without persisting."""
        _, errors = validate_definition(definition)
        return errors

    # ── Releases (immutable, D1) ──────────────────────────

    async def publish_release(
        self,
        pack_id: str,
        org_id: str,
        version: str,
        changelog: str | None,
        released_by: str,
        dependencies: dict | None = None,
    ) -> WorkflowPackRelease:
        pack = await self.get_pack(pack_id, org_id)

        if not _SEMVER_RE.match(version):
            raise AppError("INVALID_VERSION", "Version must be semver (X.Y.Z)", 422)

        # Definition must be valid and non-empty at publish time
        if not pack.definition or not pack.definition.get("steps"):
            raise AppError("EMPTY_DEFINITION", "Workflow definition has no steps", 422)
        parsed = validate_or_raise(pack.definition)

        # Dependencies validation (R7: only exact or >= constraints)
        deps = dependencies or {}
        self._validate_dependencies(deps)

        # Version uniqueness + monotonicity guidance
        existing_r = await self.db.execute(
            select(WorkflowPackRelease.version).where(WorkflowPackRelease.pack_id == pack_id)
        )
        existing_versions = [row[0] for row in existing_r.all()]
        if version in existing_versions:
            raise AppError("VERSION_EXISTS", f"Version {version} already released", 409)

        # Build the immutable manifest — ui block excluded from content (R4)
        definition_for_manifest = {
            k: v for k, v in pack.definition.items() if k != "ui"
        }
        manifest = {
            "schema_version": 1,
            "version": version,
            "name": pack.name,
            "summary": pack.summary,
            "workflow_type": pack.workflow_type,
            "definition": definition_for_manifest,
            "dependencies": deps,
            "provenance": pack.provenance or {},
        }
        canonical = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
        checksum = hashlib.sha256(canonical.encode()).hexdigest()

        release = WorkflowPackRelease(
            pack_id=pack_id,
            version=version,
            manifest=manifest,
            changelog=changelog,
            checksum=checksum,
            step_count=len(parsed.steps),
            released_by=released_by,
        )
        self.db.add(release)
        # First release publishes the pack
        if pack.status == PackStatus.DRAFT:
            pack.status = PackStatus.PUBLISHED
        try:
            await self.db.flush()
        except IntegrityError:
            raise AppError("VERSION_EXISTS", f"Version {version} already released", 409) from None

        await self._invalidate_registry_cache()
        log.info(
            "workflow_release_published",
            pack_id=pack_id,
            version=version,
            checksum=checksum[:12],
            step_count=release.step_count,
        )
        return release

    async def list_releases(self, pack_id: str, org_id: str) -> list[WorkflowPackRelease]:
        await self.get_pack(pack_id, org_id)
        result = await self.db.execute(
            select(WorkflowPackRelease).where(WorkflowPackRelease.pack_id == pack_id)
        )
        releases = list(result.scalars().all())
        releases.sort(key=lambda r: _parse_semver(r.version), reverse=True)
        return releases

    async def get_release(self, release_id: str) -> WorkflowPackRelease:
        release = await self.db.get(WorkflowPackRelease, release_id)
        if release is None:
            raise AppError("RELEASE_NOT_FOUND", "Release not found", 404)
        return release

    async def get_latest_release(self, pack_id: str) -> WorkflowPackRelease | None:
        """Latest = max semver among STABLE releases; pre-releases only when
        no stable release exists (npm dist-tag semantics — a newer 1.1.0-beta
        must not shadow the stable 1.0.0 for implicit installs/previews)."""
        result = await self.db.execute(
            select(WorkflowPackRelease).where(WorkflowPackRelease.pack_id == pack_id)
        )
        releases = list(result.scalars().all())
        if not releases:
            return None
        stable = [r for r in releases if "-" not in r.version]
        pool = stable if stable else releases
        pool.sort(key=lambda r: _parse_semver(r.version), reverse=True)
        return pool[0]

    # ── Approval workflow (mirror skill_pack) ─────────────

    async def submit_for_review(self, pack_id: str, org_id: str) -> WorkflowPack:
        pack = await self.get_pack(pack_id, org_id)
        if pack.review_status == "pending":
            raise AppError("ALREADY_PENDING", "Pack is already pending review", 409)
        if pack.review_status == "approved":
            raise AppError("ALREADY_APPROVED", "Pack is already approved", 422)
        pack.review_status = "pending"
        await self.db.flush()
        await self.db.refresh(pack)
        return pack

    async def approve_pack(self, pack_id: str, org_id: str) -> WorkflowPack:
        pack = await self.get_pack(pack_id, org_id)
        if pack.review_status != "pending":
            raise AppError("NOT_PENDING", "Pack is not pending review", 422)
        pack.review_status = "approved"
        pack.visibility = PackVisibility.PUBLIC
        await self.db.flush()
        await self.db.refresh(pack)
        await self._invalidate_registry_cache()
        return pack

    async def reject_pack(self, pack_id: str, org_id: str, reason: str | None = None) -> WorkflowPack:
        pack = await self.get_pack(pack_id, org_id)
        if pack.review_status != "pending":
            raise AppError("NOT_PENDING", "Pack is not pending review", 422)
        pack.review_status = "rejected"
        pack.rejection_reason = (reason or "")[:500] or None
        await self.db.flush()
        await self.db.refresh(pack)
        return pack

    # ── Helpers ───────────────────────────────────────────

    @staticmethod
    def _validate_dependencies(deps: dict) -> None:
        """Validate the dependencies manifest section (R7)."""
        req_caps = deps.get("requires_capabilities", [])
        rec_packs = deps.get("recommended_packs", [])
        if len(req_caps) + len(rec_packs) > MAX_DEPENDENCIES:
            raise AppError("TOO_MANY_DEPENDENCIES", f"Max {MAX_DEPENDENCIES} dependencies", 422)
        for cap in req_caps:
            if not isinstance(cap, dict) or not cap.get("capability"):
                raise AppError("INVALID_DEPENDENCY", "requires_capabilities entries need a capability key", 422)
        for rec in rec_packs:
            if not isinstance(rec, dict):
                raise AppError("INVALID_DEPENDENCY", "recommended_packs entries must be objects", 422)
            family = rec.get("family")
            if family not in ("skill_pack", "workflow_pack"):
                raise AppError(
                    "INVALID_DEPENDENCY",
                    "recommended_packs family must be skill_pack or workflow_pack",
                    422,
                )
            constraint = rec.get("version", "")
            if constraint and not _VERSION_CONSTRAINT_RE.match(constraint):
                raise AppError(
                    "INVALID_VERSION_CONSTRAINT",
                    f"Version constraint '{constraint}' must be X.Y.Z or >=X.Y.Z",
                    422,
                )

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]

    @staticmethod
    async def _invalidate_registry_cache() -> None:
        from app.core.cache import cache_delete_pattern

        await cache_delete_pattern("wfregistry:*")
