"""Component draft generation (ADR-016 Part K).

Verified external intelligence generates DRAFT artifacts only. Publishing
requires approved status plus a second explicit human action; the service
refuses draft→published in one step. Never downloads or executes external
code — ComfyUI graphs are parsed declaratively.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.catalog import CATALOG_KIND_TO_MODEL, ExternalWorkflow
from app.ecosystem.models.mapping import CapabilityMapping
from app.ecosystem.models.replacement import DRAFT_TYPES, ComponentDraft
from app.ecosystem.security import sanitize_text
from app.exceptions import AppError

_STATUS_FLOW = {
    "draft": {"in_review"},
    "in_review": {"approved", "rejected", "draft"},
    "approved": {"published", "rejected"},
    "rejected": {"draft"},
    "published": set(),
}


class DraftService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        draft_type: str,
        title: str,
        payload: dict,
        source_kind: str | None = None,
        source_id: str | None = None,
        source_observation_ids: list | None = None,
        org_id: str | None = None,
        created_by: str | None = None,
    ) -> ComponentDraft:
        if draft_type not in DRAFT_TYPES:
            raise AppError("VALIDATION_ERROR", f"Unknown draft type: {draft_type}", 422)
        draft = ComponentDraft(
            draft_type=draft_type,
            title=sanitize_text(title, 300) or "Untitled draft",
            payload=payload,
            source_kind=source_kind,
            source_id=source_id,
            source_observation_ids=source_observation_ids or [],
            validation=self._validate_payload(draft_type, payload),
            org_id=org_id,
            created_by=created_by,
        )
        self.db.add(draft)
        await self.db.flush()
        return draft

    def _validate_payload(self, draft_type: str, payload: dict) -> dict:
        errors: list[str] = []
        import json as _json

        if isinstance(payload, dict) and len(_json.dumps(payload, default=str)) > 100_000:
            raise AppError("VALIDATION_ERROR", "Draft payload too large (100k max)", 422)
        if not isinstance(payload, dict) or not payload:
            errors.append("Payload must be a non-empty object")
        elif draft_type == "workflow_pack":
            definition = payload.get("definition")
            if not isinstance(definition, dict) or not definition.get("steps"):
                errors.append("workflow_pack draft needs definition.steps")
            else:
                for i, step in enumerate(definition["steps"]):
                    if not isinstance(step, dict) or not step.get("capability"):
                        errors.append(f"Step {i} missing capability")
        elif draft_type == "skill_pack_update":
            if not payload.get("target_pack_id"):
                errors.append("skill_pack_update draft needs target_pack_id")
            if not isinstance(payload.get("suggestions"), list) or not payload["suggestions"]:
                errors.append("skill_pack_update draft needs suggestions[]")
        elif draft_type == "benchmark_suite":
            if not payload.get("family") or not payload.get("capability_key"):
                errors.append("benchmark_suite draft needs family + capability_key")
        elif draft_type == "provider_offering":
            if not payload.get("capability_key") or not payload.get("model_name"):
                errors.append("provider_offering draft needs capability_key + model_name")
        elif draft_type == "capability_mapping" and (
            not payload.get("entity_kind") or not payload.get("capability_key")
        ):
            errors.append("capability_mapping draft needs entity_kind + capability_key")
        return {"valid": not errors, "errors": errors}

    async def generate_workflow_pack_draft(
        self,
        *,
        external_workflow_id: str,
        org_id: str | None = None,
        created_by: str | None = None,
    ) -> ComponentDraft:
        """ComfyUI workflow observed → Workflow Pack draft (declarative only)."""
        workflow = await self.db.get(ExternalWorkflow, external_workflow_id)
        if not workflow:
            raise AppError("NOT_FOUND", "External workflow not found", 404)
        mappings = await self.db.scalars(
            select(CapabilityMapping).where(
                CapabilityMapping.entity_kind == "workflow",
                CapabilityMapping.entity_id == workflow.id,
            )
        )
        capability_keys = [m.capability_key for m in mappings]
        steps = [
            {
                "id": f"step_{i + 1}",
                "name": key.replace("_", " ").title(),
                "capability": key,
                "inputs": {},
                "review_gate": True,
            }
            for i, key in enumerate(capability_keys or ["image_generation"])
        ]
        payload = {
            "name": workflow.canonical_name,
            "description": workflow.description or "",
            "origin": {
                "kind": "external_workflow",
                "id": workflow.id,
                "source_repo": workflow.source_repo,
                "graph_hash": workflow.graph_hash,
            },
            "node_types": workflow.node_types or [],
            "definition": {"version": 1, "steps": steps},
            # Explicit marker: dependencies are LISTED, never installed
            "dependency_report": {
                "node_types": workflow.node_types or [],
                "auto_install": False,
            },
        }
        return await self.create(
            draft_type="workflow_pack",
            title=f"Workflow Pack draft: {workflow.canonical_name}",
            payload=payload,
            source_kind="workflow",
            source_id=workflow.id,
            org_id=org_id,
            created_by=created_by,
        )

    async def generate_skill_pack_update_draft(
        self,
        *,
        target_pack_id: str,
        deprecated_kind: str,
        deprecated_id: str,
        replacement_id: str | None = None,
        affected: list | None = None,
        created_by: str | None = None,
    ) -> ComponentDraft:
        """Structured update suggestions for a Skill Pack referencing an
        outdated tool/workflow (Part K)."""
        entity = await self.db.get(
            CATALOG_KIND_TO_MODEL.get(deprecated_kind, ExternalWorkflow), deprecated_id
        )
        entity_name = getattr(entity, "canonical_name", deprecated_id)
        suggestions = [
            {
                "kind": item.get("kind", "lesson"),
                "ref": item.get("ref"),
                "issue": f"References deprecated {deprecated_kind} {entity_name}",
                "proposed_replacement_id": replacement_id,
            }
            for item in (affected or [{"kind": "lesson", "ref": None}])
        ]
        payload = {
            "target_pack_id": target_pack_id,
            "deprecated": {"kind": deprecated_kind, "id": deprecated_id, "name": entity_name},
            "suggestions": suggestions,
        }
        return await self.create(
            draft_type="skill_pack_update",
            title=f"Skill Pack update: replace {entity_name}",
            payload=payload,
            source_kind=deprecated_kind,
            source_id=deprecated_id,
            created_by=created_by,
        )

    # ── Review workflow ─────────────────────────────────────────────

    async def get(self, draft_id: str, *, org_id: str | None = None) -> ComponentDraft:
        draft = await self.db.get(ComponentDraft, draft_id)
        if not draft:
            raise AppError("NOT_FOUND", "Draft not found", 404)
        # Org-scoped drafts: uniform 404 outside the org (no existence oracle)
        if draft.org_id is not None and org_id is not None and draft.org_id != org_id:
            raise AppError("NOT_FOUND", "Draft not found", 404)
        return draft

    async def list(
        self,
        *,
        draft_type: str | None = None,
        status: str | None = None,
        org_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ComponentDraft]:
        from sqlalchemy import or_

        query = select(ComponentDraft)
        if draft_type:
            query = query.where(ComponentDraft.draft_type == draft_type)
        if status:
            query = query.where(ComponentDraft.status == status)
        query = query.where(
            or_(ComponentDraft.org_id.is_(None), ComponentDraft.org_id == org_id)
            if org_id
            else ComponentDraft.org_id.is_(None)
        )
        rows = await self.db.scalars(
            query.order_by(ComponentDraft.created_at.desc()).limit(limit).offset(offset)
        )
        return list(rows)

    async def transition(
        self, draft_id: str, *, to_status: str, actor_id: str, org_id: str | None = None
    ) -> ComponentDraft:
        draft = await self.get(draft_id, org_id=org_id)
        # Row lock: two concurrent publishes must serialize — the loser then
        # re-reads "published" and is refused by the state machine, so the
        # materialization side effect (_publish) can never run twice.
        await self.db.refresh(draft, with_for_update=True)
        if to_status not in _STATUS_FLOW.get(draft.status, set()):
            code = (
                "ECO_DRAFT_NOT_APPROVED"
                if to_status == "published"
                else "ECO_INVALID_TRANSITION"
            )
            raise AppError(code, f"Cannot move draft {draft.status} -> {to_status}", 409)
        # §17 four-eyes (checked AFTER transition validity — the state machine
        # answers "is this move legal", four-eyes answers "may YOU make it"):
        # the draft creator can neither approve nor publish their own draft;
        # submit/reject/edit stay self-service.
        if (
            to_status in ("approved", "published")
            and draft.created_by is not None
            and actor_id == draft.created_by
        ):
            raise AppError(
                "ECO_FOUR_EYES",
                "Draft creator cannot approve or publish their own draft",
                409,
            )
        if to_status == "published":
            if not (draft.validation or {}).get("valid"):
                raise AppError("ECO_DRAFT_NOT_APPROVED", "Draft failed validation", 409)
            draft.published_ref = await self._publish(draft, actor_id)
        if to_status in ("approved", "rejected"):
            draft.reviewed_by = actor_id
            draft.reviewed_at = datetime.now(UTC)
        draft.status = to_status
        await self.db.flush()
        return draft

    async def update_payload(
        self, draft_id: str, *, payload: dict, org_id: str | None = None
    ) -> ComponentDraft:
        draft = await self.get(draft_id, org_id=org_id)
        if draft.status not in ("draft", "in_review"):
            raise AppError("ECO_INVALID_TRANSITION", "Only editable while draft/in_review", 409)
        draft.payload = payload
        draft.validation = self._validate_payload(draft.draft_type, payload)
        # GitHub "new commits dismiss review" semantics: editing while
        # in_review invalidates the review basis — the draft drops back to
        # draft status so it must be re-submitted and re-read. Closes the
        # TOCTOU window between a reviewer reading and approving.
        if draft.status == "in_review":
            draft.status = "draft"
        await self.db.flush()
        return draft

    async def _publish(self, draft: ComponentDraft, actor_id: str) -> str | None:
        """Materialize the approved draft into a product entity (still unpublished
        product-side: workflow packs are created in DRAFT product status)."""
        if draft.draft_type == "workflow_pack":
            from app.models.skill_pack import PackStatus, PackVisibility
            from app.models.workflow_pack import WorkflowPack

            if not draft.org_id:
                raise AppError(
                    "VALIDATION_ERROR", "workflow_pack drafts need an owning org", 422
                )
            payload = draft.payload or {}
            name = (payload.get("name") or draft.title)[:200]
            slug = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")[:180]
            pack = WorkflowPack(
                owner_org_id=draft.org_id,
                name=name,
                slug=f"{slug}-{draft.id[-6:].lower()}",
                description=payload.get("description"),
                # Product-side the pack starts as a PRIVATE DRAFT — publishing
                # the eco draft never publishes the pack itself
                status=PackStatus.DRAFT,
                visibility=PackVisibility.PRIVATE,
                provenance={"eco_draft_id": draft.id, "origin": payload.get("origin", {})},
                definition=payload.get("definition", {}),
                created_by=actor_id,
            )
            self.db.add(pack)
            await self.db.flush()
            return pack.id
        if draft.draft_type == "benchmark_suite":
            from app.ecosystem.services.benchmark import BenchmarkService

            payload = draft.payload or {}
            suite = await BenchmarkService(self.db).create_suite(
                key=payload.get("key") or f"draft-{draft.id.lower()}",
                name=payload.get("name", draft.title)[:200],
                family=payload["family"],
                capability_key=payload["capability_key"],
                description=payload.get("description"),
                rubric=payload.get("rubric"),
                created_by=actor_id,
            )
            return suite.id
        # Other draft types publish as structured suggestions (no side effects)
        return None
