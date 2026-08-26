"""Production solution composer (ADR-013, Issue #21 Part F).

Composes a DRAFT production solution: a chain of I/O-compatible Workflow
Packs + a Project Template + capability requirements + recommended skill
packs. Incompatible types and unresolved inputs are surfaced as first-class
placeholders — the composer never silently inserts conversions (red line).

A human confirm materializes a real Project from the matched template.
"""

from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.composer import SolutionDraft
from app.models.project import Project
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack
from app.models.workflow_pack import WorkflowPack
from app.services.matching import ENGINE_VERSION, MatchingEngine, MatchSpec
from app.services.requirement_profile import RequirementProfileService

log = structlog.get_logger()

MAX_CHAIN_LENGTH = 4
# Asset types require identity-producing upstream packs; text-ish inputs come
# from the user directly (mirrors the definition coercion matrix)
_ASSET_TYPES = {"image", "video", "audio", "reference_asset"}
_USER_TYPES = {"text", "prompt", "selection", "json"}


class ProductionComposerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Compose ───────────────────────────────────────────

    async def compose(self, org_id: str, profile_id: str, created_by: str) -> SolutionDraft:
        profile_svc = RequirementProfileService(self.db)
        profile = await profile_svc.get_profile(profile_id, org_id)
        if profile.status != "confirmed":
            raise AppError(
                "PROFILE_NOT_CONFIRMED",
                "Requirement profile must be confirmed before composing",
                422,
            )
        requirement = RequirementProfileService.build_match_requirement(profile)

        engine = MatchingEngine(self.db)
        run, results, _ = await engine.run(
            MatchSpec(
                org_id=org_id,
                target_entity_type="workflow_pack",
                requirement=requirement,
                context_type=profile.context_type.value,
                requirement_profile_id=profile.id,
                created_by=created_by,
                limit=50,
                record_impressions=False,  # composer-internal run — user never sees this list
            )
        )
        ranked_ids = [r.entity_id for r in results if r.rank is not None]
        packs_by_id: dict[str, WorkflowPack] = {}
        if ranked_ids:
            packs_r = await self.db.execute(
                select(WorkflowPack).where(WorkflowPack.id.in_(ranked_ids))
            )
            packs_by_id = {p.id: p for p in packs_r.scalars().all()}
        ranked_packs = [packs_by_id[pid] for pid in ranked_ids if pid in packs_by_id]

        gaps: list[dict] = []
        placeholders: list[dict] = []

        # ── Chain assembly by output-type back-matching ──
        target_type = requirement.get("output_type") or requirement.get("_soft_output_type")
        chain: list[WorkflowPack] = []
        if ranked_packs:
            head = None
            if target_type:
                head = next(
                    (
                        p
                        for p in ranked_packs
                        if any(o.get("type") == target_type for o in (p.output_schema or []))
                    ),
                    None,
                )
                if head is None:
                    gaps.append({"code": "NO_WORKFLOW_FOR_OUTPUT", "output_type": target_type})
            if head is None:
                head = ranked_packs[0]
            chain = [head]
            used = {head.id}

            # Walk unresolved asset inputs backwards, chaining producers
            frontier = list(head.input_schema or [])
            while frontier and len(chain) < MAX_CHAIN_LENGTH:
                inp = frontier.pop(0)
                itype = inp.get("type")
                required = inp.get("required", True)
                if itype in _USER_TYPES:
                    placeholders.append(
                        {
                            "input_key": inp.get("key"),
                            "type": itype,
                            "reason": "needs_user_value",
                        }
                    )
                    continue
                if itype not in _ASSET_TYPES or not required:
                    continue
                producer = next(
                    (
                        p
                        for p in ranked_packs
                        if p.id not in used
                        and any(o.get("type") == itype for o in (p.output_schema or []))
                    ),
                    None,
                )
                if producer is None:
                    placeholders.append(
                        {"input_key": inp.get("key"), "type": itype, "reason": "no_producer"}
                    )
                    continue
                chain.append(producer)
                used.add(producer.id)
                frontier.extend(producer.input_schema or [])

            # Chain hit MAX_CHAIN_LENGTH with unresolved inputs left on the
            # frontier — surface them as placeholders, never drop silently
            # (red line: incompatibilities are first-class placeholders).
            for inp in frontier:
                itype = inp.get("type")
                if itype in _ASSET_TYPES and inp.get("required", True):
                    placeholders.append(
                        {
                            "input_key": inp.get("key"),
                            "type": itype,
                            "reason": "chain_length_cap",
                        }
                    )
                elif itype in _USER_TYPES:
                    placeholders.append(
                        {
                            "input_key": inp.get("key"),
                            "type": itype,
                            "reason": "needs_user_value",
                        }
                    )
        else:
            gaps.append({"code": "NO_WORKFLOWS_AVAILABLE"})

        # Chain runs producer-first
        chain.reverse()

        # ── Project template match ──
        template_entry = None
        try:
            _t_run, t_results, _ = await engine.run(
                MatchSpec(
                    org_id=org_id,
                    target_entity_type="project_template",
                    requirement=requirement,
                    context_type=profile.context_type.value,
                    requirement_profile_id=profile.id,
                    created_by=created_by,
                    limit=1,
                    record_impressions=False,  # composer-internal run
                )
            )
            ranked_templates = [r for r in t_results if r.rank is not None]
            if ranked_templates:
                from app.models.project import ProjectTemplate

                tmpl = await self.db.get(ProjectTemplate, ranked_templates[0].entity_id)
                if tmpl is not None:
                    template_entry = {"entity_id": tmpl.id, "name": tmpl.name}
        except AppError:
            pass
        if template_entry is None:
            gaps.append({"code": "NO_TEMPLATE_AVAILABLE"})

        # ── Capability roll-up from latest release manifests ──
        from app.services.provider import ProviderService
        from app.services.workflow_pack import WorkflowPackService

        wf_svc = WorkflowPackService(self.db)
        required_caps: list[dict] = []
        seen_caps: set[str] = set()
        recommended_slugs: list[dict] = []
        for pack in chain:
            release = await wf_svc.get_latest_release(pack.id)
            if release is None:
                gaps.append({"code": "NO_RELEASES", "entity_id": pack.id, "name": pack.name})
                continue
            deps = (release.manifest or {}).get("dependencies", {})
            # Manifest-tolerant like check_capabilities: a non-dict entry
            # (str/int — pre-gate manifests or future write paths) must not
            # AttributeError into a 500 before the hardened checker even runs
            raw_caps = deps.get("requires_capabilities", [])
            for cap in raw_caps if isinstance(raw_caps, list) else []:
                if not isinstance(cap, dict):
                    continue  # check_capabilities reports MALFORMED_REQUIREMENT
                key = cap.get("capability", "")
                if isinstance(key, str) and key and key not in seen_caps:
                    seen_caps.add(key)
                    required_caps.append(cap)
            raw_recs = deps.get("recommended_packs", [])
            for rec in raw_recs if isinstance(raw_recs, list) else []:
                if isinstance(rec, dict) and rec.get("family") == "skill_pack":
                    recommended_slugs.append(rec)

        provider_gaps = await ProviderService(self.db).check_capabilities(org_id, required_caps)
        for pg in provider_gaps:
            # CAPABILITY_UNSATISFIED maps to the composer's vocabulary
            # (NO_ELIGIBLE_PROVIDER drives the frontend's connect-a-provider
            # prompt); other checker codes (MALFORMED_REQUIREMENT) pass
            # through — blanket-overwriting rendered a nonsense provider
            # prompt for malformed manifests
            if pg.get("code") == "CAPABILITY_UNSATISFIED":
                gaps.append({**pg, "code": "NO_ELIGIBLE_PROVIDER"})
            else:
                gaps.append(pg)

        # ── Recommended skill packs (resolve by slug; skip unresolvable) ──
        items: list[dict] = []
        seen_rec: set[str] = set()
        for rec in recommended_slugs:
            slug = rec.get("slug", "")
            if not slug or slug in seen_rec:
                continue
            seen_rec.add(slug)
            # Deterministic pick among same-slug packs: own-org pack wins,
            # then oldest (ULID asc) — slug is only unique per owner org.
            sp_r = await self.db.execute(
                select(SkillPack)
                .where(SkillPack.slug == slug, SkillPack.status == PackStatus.PUBLISHED)
                .order_by(SkillPack.id.asc())
            )
            candidates = list(sp_r.scalars().all())
            chosen = next(
                (sp for sp in candidates if sp.owner_org_id == org_id),
                next(
                    (
                        sp
                        for sp in candidates
                        if sp.visibility in (PackVisibility.PUBLIC, PackVisibility.UNLISTED)
                    ),
                    None,
                ),
            )
            if chosen is not None:
                items.append(
                    {
                        "family": "skill_pack",
                        "entity_id": chosen.id,
                        "name": chosen.name,
                        "required": False,
                        "status": "included",
                    }
                )

        payload = {
            "workflow_chain": [
                {
                    "entity_id": p.id,
                    "name": p.name,
                    "order": i,
                    "outputs": p.output_schema or [],
                    "inputs": p.input_schema or [],
                }
                for i, p in enumerate(chain)
            ],
            "template": template_entry,
            "items": items,
            "placeholders": placeholders,
            "gaps": gaps,
            "required_capabilities": required_caps,
            "match_run_id": run.id,
        }
        from app.services.learning_composer import check_draft_payload_size

        check_draft_payload_size(payload)
        draft = SolutionDraft(
            org_id=org_id,
            draft_type="production_solution",
            requirement_profile_id=profile.id,
            match_run_id=run.id,
            payload=payload,
            engine_version=ENGINE_VERSION,
            created_by=created_by,
        )
        self.db.add(draft)
        await self.db.flush()
        log.info(
            "production_draft_composed",
            draft_id=draft.id,
            org_id=org_id,
            chain_length=len(chain),
            gaps=len(gaps),
        )
        return draft

    # ── Confirm (materialize a Project) ───────────────────

    async def confirm(self, draft_id: str, org_id: str, confirmed_by: str) -> Project:
        from app.services.learning_composer import LearningComposerService

        composer_svc = LearningComposerService(self.db)
        draft = await composer_svc.get_draft(draft_id, org_id)
        if draft.draft_type != "production_solution":
            raise AppError("WRONG_DRAFT_TYPE", "Draft is not a production-solution draft", 422)
        # Conditional-UPDATE claim BEFORE materialization (race-safe: the
        # loser of two concurrent confirms gets rowcount 0 → 409)
        await composer_svc.claim_draft_for_confirm(draft_id, org_id)
        try:
            return await self._materialize(draft, org_id, confirmed_by)
        except BaseException:
            # Revert the claim so the draft isn't stuck in 'confirming'
            try:
                await composer_svc.release_draft_claim(draft_id)
            except Exception:
                # Session unusable (aborted transaction) — rolling back also
                # discards the uncommitted claim, so the draft stays 'draft'.
                await self.db.rollback()
            raise

    async def _materialize(
        self, draft: SolutionDraft, org_id: str, confirmed_by: str
    ) -> Project:
        from app.services.project import ProjectService

        draft_id = draft.id
        template = (draft.payload or {}).get("template")
        if not template:
            raise AppError(
                "NO_TEMPLATE_IN_DRAFT",
                "Draft has no project template to materialize from",
                422,
            )

        project = await ProjectService(self.db).create_project_from_template(
            org_id=org_id,
            template_id=template["entity_id"],
            created_by=confirmed_by,
        )
        # Provenance: record the composed workflow chain (traceability)
        wf_ids = [w["entity_id"] for w in (draft.payload or {}).get("workflow_chain", [])]
        if wf_ids:
            wf_names = ", ".join(
                w["name"] for w in (draft.payload or {}).get("workflow_chain", [])
            )
            project.description = (
                f"{project.description}\n\n---\nComposed from workflows: {wf_names} "
                f"(draft {draft.id})"
            )

        draft.status = "confirmed"
        draft.confirmed_by = confirmed_by
        draft.confirmed_at = datetime.now(UTC)
        draft.materialized_entity_id = project.id
        await self.db.flush()
        log.info("production_draft_confirmed", draft_id=draft_id, project_id=project.id)
        return project
