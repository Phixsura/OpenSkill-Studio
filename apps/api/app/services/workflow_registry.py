"""Public workflow-pack registry — search, browse, preview (ADR-010).

Mirrors app/services/registry.py: Redis caches only {ids, total} and cache
hits re-apply access-control filters so stale entries can never serve
archived/private/rejected packs.
"""

import copy
import hashlib

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.exceptions import AppError
from app.models.skill_pack import PackStatus, PackVisibility
from app.models.workflow_pack import WorkflowPack, WorkflowPackRelease
from app.services.workflow_pack import _parse_semver

log = structlog.get_logger()


def _public_filters(query):
    return query.where(
        WorkflowPack.visibility == PackVisibility.PUBLIC,
        WorkflowPack.status == PackStatus.PUBLISHED,
        or_(
            WorkflowPack.review_status.is_(None),
            WorkflowPack.review_status == "approved",
        ),
    )


class WorkflowRegistryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_packs(
        self,
        search: str | None = None,
        scenario: str | None = None,
        tool: str | None = None,
        capability: str | None = None,
        workflow_type: str | None = None,
        input_type: str | None = None,
        output_type: str | None = None,
        sort: str = "newest",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[WorkflowPack], int]:
        """Search public, published workflow packs. Cached 5 minutes."""
        # ── Cache check (ids-only payload; access control re-applied on hit) ──
        cache_key_src = (
            f"{search}:{scenario}:{tool}:{capability}:{workflow_type}:"
            f"{input_type}:{output_type}:{sort}:{page}:{per_page}"
        )
        cache_key = f"wfregistry:search:{hashlib.md5(cache_key_src.encode()).hexdigest()}"
        cached = await cache_get(cache_key)
        if cached is not None:
            pack_ids = cached.get("ids", [])
            if pack_ids:
                result = await self.db.execute(
                    _public_filters(select(WorkflowPack).where(WorkflowPack.id.in_(pack_ids)))
                )
                packs_by_id = {p.id: p for p in result.scalars().all()}
                filtered = [packs_by_id[pid] for pid in pack_ids if pid in packs_by_id]
                # Return the cached TOTAL (across all pages), not the page
                # size — otherwise has_more computes False and pagination
                # stops at page 1 for the cache TTL.
                return filtered, cached.get("total", len(filtered))
            return [], 0

        # ── Build query ──
        base = _public_filters(select(WorkflowPack))

        if search and search.strip():
            escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            term = f"%{escaped}%"
            base = base.where(
                or_(
                    WorkflowPack.name.ilike(term),
                    WorkflowPack.summary.ilike(term),
                    WorkflowPack.description.ilike(term),
                )
            )
        if scenario:
            base = base.where(WorkflowPack.scenario_tags.contains([scenario]))
        if tool:
            base = base.where(WorkflowPack.tool_tags.contains([tool]))
        if capability:
            base = base.where(WorkflowPack.capability_tags.contains([capability]))
        if workflow_type:
            base = base.where(WorkflowPack.workflow_type == workflow_type)

        if sort == "most_installed":
            base = base.order_by(WorkflowPack.install_count.desc())
        elif sort == "name":
            base = base.order_by(WorkflowPack.name.asc())
        else:  # newest
            base = base.order_by(WorkflowPack.created_at.desc())

        # input/output type filters require inspecting the derived JSONB
        # schemas. The workflow catalog stays small (<1k packs for years) so
        # we filter in Python when either filter is present — simpler and
        # correct vs. a fragile JSONB path predicate.
        if input_type or output_type:
            result = await self.db.execute(base)
            all_packs = list(result.scalars().all())
            filtered = [
                p
                for p in all_packs
                if (
                    not input_type
                    or any(i.get("type") == input_type for i in (p.input_schema or []))
                )
                and (
                    not output_type
                    or any(o.get("type") == output_type for o in (p.output_schema or []))
                )
            ]
            total = len(filtered)
            packs = filtered[(page - 1) * per_page : page * per_page]
        else:
            total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
            total = total_r.scalar_one()
            result = await self.db.execute(
                base.offset((page - 1) * per_page).limit(per_page)
            )
            packs = list(result.scalars().all())

        await cache_set(cache_key, {"ids": [p.id for p in packs], "total": total}, ttl=300)
        return packs, total

    async def get_public_pack(self, pack_id: str) -> WorkflowPack:
        """Get a public or unlisted workflow pack by ID."""
        pack = await self.db.get(WorkflowPack, pack_id)
        if pack is None or pack.status != PackStatus.PUBLISHED:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)
        if pack.visibility == PackVisibility.PRIVATE:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)
        # PUBLIC packs must pass review (mirror _public_filters / list path)
        if pack.visibility == PackVisibility.PUBLIC and pack.review_status not in (
            None,
            "approved",
        ):
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)
        return pack

    async def get_public_releases(self, pack_id: str) -> list[WorkflowPackRelease]:
        await self.get_public_pack(pack_id)  # verify accessible
        result = await self.db.execute(
            select(WorkflowPackRelease).where(WorkflowPackRelease.pack_id == pack_id)
        )
        releases = list(result.scalars().all())
        releases.sort(key=lambda r: _parse_semver(r.version), reverse=True)
        return releases

    async def get_pack_preview(self, pack_id: str) -> dict:
        """Structural preview from the latest release — definition without ui block."""
        await self.get_public_pack(pack_id)
        result = await self.db.execute(
            select(WorkflowPackRelease).where(WorkflowPackRelease.pack_id == pack_id)
        )
        releases = list(result.scalars().all())
        if not releases:
            raise AppError("NO_RELEASES", "This pack has no releases yet", 404)
        # Public preview shows the latest STABLE release; pre-releases only
        # when nothing stable exists (a 1.1.0-beta must not shadow 1.0.0)
        stable = [r for r in releases if "-" not in r.version]
        pool = stable if stable else releases
        latest = max(pool, key=lambda r: _parse_semver(r.version))
        manifest = latest.manifest or {}
        definition = copy.deepcopy(
            {k: v for k, v in (manifest.get("definition") or {}).items() if k != "ui"}
        )
        # Strip org-internal binding details from the anonymous preview —
        # pinned offerings / binding modes leak the author org's provider setup
        for step in definition.get("steps", []) or []:
            config = step.get("config")
            if isinstance(config, dict):
                config.pop("pinned_offering_id", None)
                config.pop("binding_mode", None)
        deps = manifest.get("dependencies") or {}
        return {
            "version": latest.version,
            "definition": definition,
            "step_count": latest.step_count,
            "inputs": definition.get("inputs", []),
            "outputs": definition.get("outputs", []),
            "requires_capabilities": deps.get("requires_capabilities", []),
            "recommended_packs": deps.get("recommended_packs", []),
        }
