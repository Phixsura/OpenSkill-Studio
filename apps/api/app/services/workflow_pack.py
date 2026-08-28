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


def _parse_semver(version: str) -> tuple:
    """Parse 'X.Y.Z' or 'X.Y.Z-prerelease' into a comparable tuple.

    Prerelease precedence follows semver 2.0 §11: identifiers are compared
    dot-by-dot, numeric identifiers compare NUMERICALLY (rc.10 > rc.9 — a
    plain string key would sort them lexicographically) and rank below any
    alphanumeric identifier; a longer identifier list wins a shared prefix.
    A release without prerelease ranks above every prerelease of the same
    X.Y.Z, so the key's fourth element is (1,) for releases and
    (0, *identifiers) for prereleases.
    """
    base, _, prerelease = version.partition("-")
    parts = base.split(".")
    if not prerelease:
        pre_key: tuple = (1,)
    else:
        identifiers = tuple(
            (0, int(ident), "") if ident.isdigit() else (1, 0, ident)
            for ident in prerelease.split(".")
        )
        pre_key = (0, *identifiers)
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
            try:
                parsed_status = PackStatus(status)
            except ValueError:
                raise AppError("INVALID_STATUS", f"Unknown status '{status}'", 422) from None
            query = query.where(WorkflowPack.status == parsed_status)
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

    async def get_pack(
        self, pack_id: str, org_id: str, for_update: bool = False
    ) -> WorkflowPack:
        # for_update: take a row lock and REFRESH the in-memory attributes to
        # committed state (populate_existing) for callers that then mutate on
        # a read-check-write basis. Without it, every workflow_pack mutation
        # (update_pack / approve / reject / delete / publish / update_definition)
        # was a stale db.get snapshot + unguarded ORM setattr under READ
        # COMMITTED — two concurrent writers each decided on pre-mutation state
        # and last-writer-won. Reproduced (R70): approve overwrites a committed
        # reject; publish resurrects a just-archived pack; and most seriously an
        # approval BYPASS — update_pack(visibility=public) passing its stale
        # 'approved' gate while a concurrent update_definition had already reset
        # review_status to None, publishing an unapproved pack to the registry.
        # FOR UPDATE serializes them: the loser blocks, then re-reads fresh
        # state so its own gate/status checks see the committed value.
        if for_update:
            result = await self.db.execute(
                select(WorkflowPack)
                .where(WorkflowPack.id == pack_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            pack = result.scalar_one_or_none()
        else:
            pack = await self.db.get(WorkflowPack, pack_id)
        if pack is None or pack.owner_org_id != org_id or pack.status == PackStatus.ARCHIVED:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)
        return pack

    async def update_pack(self, pack_id: str, org_id: str, **fields) -> WorkflowPack:
        pack = await self.get_pack(pack_id, org_id, for_update=True)
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
        # Registry-facing card fields: changing any of them on an APPROVED
        # pack voids the approval, same as a definition change — otherwise an
        # innocuous pack gets approved and the public card content is swapped
        # past the review gate (name/summary/tags rewrite with approved kept).
        _card_fields = (
            "name", "summary", "description", "scenario_tags",
            "tool_tags", "difficulty", "workflow_type", "cover_image_key",
        )
        card_changed = any(
            key in _card_fields and value is not None and getattr(pack, key, None) != value
            for key, value in fields.items()
        )
        for key, value in fields.items():
            if value is not None and hasattr(pack, key):
                setattr(pack, key, value)
        if card_changed and pack.review_status == "approved":
            pack.review_status = None
            if pack.visibility == PackVisibility.PUBLIC:
                pack.visibility = PackVisibility.UNLISTED
            log.info(
                "workflow_pack_approval_reset_on_card_change",
                pack_id=pack_id,
                org_id=org_id,
            )
        try:
            await self.db.flush()
        except IntegrityError:
            raise AppError("SLUG_CONFLICT", "A pack with this name already exists", 409) from None
        await self.db.refresh(pack)
        await self._invalidate_registry_cache()
        return pack

    async def delete_pack(self, pack_id: str, org_id: str) -> None:
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        pack.status = PackStatus.ARCHIVED
        await self.db.flush()
        await self._invalidate_registry_cache()
        log.info("workflow_pack_archived", pack_id=pack_id, org_id=org_id)

    # ── Definition ────────────────────────────────────────

    async def update_definition(self, pack_id: str, org_id: str, definition: dict) -> WorkflowPack:
        """Update the working definition. Draft-editable only; releases are immutable."""
        pack = await self.get_pack(pack_id, org_id, for_update=True)
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
        # schemas, capability tags). An approved pack must re-enter review so
        # the public card can never drift from what was approved — REGARDLESS
        # of current visibility, or an unlisted detour (public → unlisted →
        # edit definition → public) would carry 'approved' past the gate.
        if pack.review_status == "approved":
            pack.review_status = None
            if pack.visibility == PackVisibility.PUBLIC:
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
        pack = await self.get_pack(pack_id, org_id, for_update=True)

        if not _SEMVER_RE.match(version):
            raise AppError("INVALID_VERSION", "Version must be semver (X.Y.Z)", 422)

        # Definition must be valid and non-empty at publish time
        if not pack.definition or not pack.definition.get("steps"):
            raise AppError("EMPTY_DEFINITION", "Workflow definition has no steps", 422)
        parsed = validate_or_raise(pack.definition)

        # Dependencies validation (R7: only exact or >= constraints)
        deps = dict(dependencies or {})
        self._validate_dependencies(deps)
        # requires_capabilities is DERIVED from the definition's
        # provider_action steps, merged with (never replaced by) the caller's
        # declaration. Trusting the client list alone lets a publisher omit
        # a capability → the install gate (ADR-011 CAPABILITY_UNSATISFIED)
        # silently passes for orgs with no matching provider, and the
        # failure surfaces only at run time as a mid-run
        # NO_ELIGIBLE_PROVIDER step failure — exactly what the gate exists
        # to catch before install. Features union per capability: the gate
        # checks feature-superset offerings, so under-declaring features
        # has the same bypass effect as omitting the capability.
        declared: dict[str, set[str]] = {}
        for cap in deps.get("requires_capabilities", []) or []:
            key = cap.get("capability")
            feats = {f for f in cap.get("features", []) if isinstance(f, str)}
            declared.setdefault(key, set()).update(feats)
        for step in parsed.steps:
            if step.type != "provider_action":
                continue
            key = step.config.get("capability")
            if not key:
                continue
            feats = {
                f
                for f in step.config.get("required_features", [])
                if isinstance(f, str)
            }
            declared.setdefault(key, set()).update(feats)
        deps["requires_capabilities"] = [
            {"capability": key, "features": sorted(feats)}
            for key, feats in sorted(declared.items())
        ]

        # Version uniqueness + monotonicity guidance
        existing_r = await self.db.execute(
            select(WorkflowPackRelease.version).where(WorkflowPackRelease.pack_id == pack_id)
        )
        existing_versions = [row[0] for row in existing_r.all()]
        if version in existing_versions:
            raise AppError("VERSION_EXISTS", f"Version {version} already released", 409)

        # Build the immutable manifest — ui block excluded from content (R4).
        # Also strip ORG-LOCAL binding hints from every provider_action step:
        # pinned_offering_id points at THIS org's offering row, so a pinned
        # release would (a) fail every cross-org install — the installer's
        # _resolve_offering rejects an offering whose connection.org_id !=
        # run.org_id → NO_ELIGIBLE_PROVIDER on every run, and (b) leak the
        # author org's provider setup (the registry preview strips these for
        # exactly this reason, but the distributed manifest did not).
        # Binding is an INSTALL-TIME per-org decision (workflow_step_bindings),
        # never baked into the shared release.
        import copy as _copy

        definition_for_manifest = _copy.deepcopy(
            {k: v for k, v in pack.definition.items() if k != "ui"}
        )
        for _step in definition_for_manifest.get("steps", []):
            _cfg = _step.get("config")
            if isinstance(_cfg, dict) and _step.get("type") == "provider_action":
                _cfg.pop("pinned_offering_id", None)
                # binding_mode resets to the default "auto" — a pinned/preferred
                # mode without the org-local offering id is meaningless downstream
                if _cfg.get("binding_mode") in ("pinned", "preferred"):
                    _cfg["binding_mode"] = "auto"
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
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        if pack.review_status == "pending":
            raise AppError("ALREADY_PENDING", "Pack is already pending review", 409)
        if pack.review_status == "approved":
            raise AppError("ALREADY_APPROVED", "Pack is already approved", 422)
        pack.review_status = "pending"
        await self.db.flush()
        await self.db.refresh(pack)
        return pack

    async def approve_pack(self, pack_id: str, org_id: str) -> WorkflowPack:
        pack = await self.get_pack(pack_id, org_id, for_update=True)
        if pack.review_status != "pending":
            raise AppError("NOT_PENDING", "Pack is not pending review", 422)
        pack.review_status = "approved"
        pack.visibility = PackVisibility.PUBLIC
        await self.db.flush()
        await self.db.refresh(pack)
        await self._invalidate_registry_cache()
        return pack

    async def reject_pack(self, pack_id: str, org_id: str, reason: str | None = None) -> WorkflowPack:
        pack = await self.get_pack(pack_id, org_id, for_update=True)
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
        """Validate the dependencies manifest section (R7).

        Type-checks before any len()/iteration — arbitrary JSON values
        (ints, strings, dicts) must 422, not TypeError into a 500. This is
        the publish-side gate that also protects install-side readers.
        """
        req_caps = deps.get("requires_capabilities", [])
        rec_packs = deps.get("recommended_packs", [])
        if not isinstance(req_caps, list):
            raise AppError("INVALID_DEPENDENCY", "requires_capabilities must be a list", 422)
        if not isinstance(rec_packs, list):
            raise AppError("INVALID_DEPENDENCY", "recommended_packs must be a list", 422)
        if len(req_caps) + len(rec_packs) > MAX_DEPENDENCIES:
            raise AppError("TOO_MANY_DEPENDENCIES", f"Max {MAX_DEPENDENCIES} dependencies", 422)
        for cap in req_caps:
            if not isinstance(cap, dict):
                raise AppError("INVALID_DEPENDENCY", "requires_capabilities entries must be objects", 422)
            capability = cap.get("capability")
            if not isinstance(capability, str) or not capability or len(capability) > 64:
                raise AppError(
                    "INVALID_DEPENDENCY",
                    "requires_capabilities entries need a capability key (non-empty string, max 64 chars)",
                    422,
                )
            features = cap.get("features", [])
            if not isinstance(features, list) or len(features) > 20:
                raise AppError("INVALID_DEPENDENCY", "features must be a list of max 20 items", 422)
            for feature in features:
                if not isinstance(feature, str) or len(feature) > 64:
                    raise AppError(
                        "INVALID_DEPENDENCY", "features entries must be strings of max 64 chars", 422
                    )
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
            # isinstance before .match — a non-string constraint (int, list)
            # would TypeError into a 500, the exact class this gate closes
            if constraint and (
                not isinstance(constraint, str) or not _VERSION_CONSTRAINT_RE.match(constraint)
            ):
                raise AppError(
                    "INVALID_VERSION_CONSTRAINT",
                    f"Version constraint '{constraint}' must be X.Y.Z or >=X.Y.Z",
                    422,
                )
            slug = rec.get("slug", "")
            if slug and (not isinstance(slug, str) or len(slug) > 200):
                raise AppError(
                    "INVALID_DEPENDENCY", "recommended_packs slug must be a string of max 200 chars", 422
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
