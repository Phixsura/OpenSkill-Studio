"""Transitive impact analysis (ADR-016 Part I).

Cycle-safe BFS over reversed dependency edges with depth/node caps. Results
are stored (analysis + items) so the operator UI can show what changed,
provenance, affected components, active usage and recommended action.
"""

from collections import deque
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.graph import (
    IMPACT_CLASSIFICATIONS,
    IMPACT_MAX_DEPTH,
    IMPACT_MAX_NODES,
    DependencyEdge,
    ImpactAnalysis,
    ImpactItem,
)
from app.ecosystem.models.observation import ChangeEvent
from app.exceptions import AppError

# Change severity → impact classification (identical vocabulary by design)
_SEVERITY_TO_CLASSIFICATION = {
    "info": "informational",
    "update_available": "update_available",
    "degraded": "degraded",
    "breaking": "breaking",
    "security_critical": "security_critical",
    "sunset_risk": "sunset_risk",
}

# Classification → default recommended action for affected components
_CLASSIFICATION_ACTION = {
    "informational": "none",
    "update_available": "review",
    "degraded": "review",
    "breaking": "update",
    "security_critical": "block",
    "sunset_risk": "migrate",
}


class ImpactService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compute(self, change_event_id: str) -> ImpactAnalysis:
        """Compute and store the transitive impact of one change event."""
        change = await self.db.get(ChangeEvent, change_event_id)
        if not change:
            raise AppError("NOT_FOUND", "Change event not found", 404)
        if not change.canonical_entity_id or not change.entity_kind:
            raise AppError(
                "ECO_MERGE_CONFIRMATION_REQUIRED",
                "Change event is not linked to a canonical entity yet",
                409,
            )
        classification = _SEVERITY_TO_CLASSIFICATION.get(change.severity, "informational")
        root_kind, root_id = change.entity_kind, change.canonical_entity_id

        # Deadline from the change payload if it carries a sunset date
        deadline = None
        new_val = change.new_value or {}
        sunset_raw = new_val.get("sunset_at") if isinstance(new_val, dict) else None
        if isinstance(sunset_raw, str):
            try:
                deadline = datetime.fromisoformat(sunset_raw.replace("Z", "+00:00"))
                if deadline.tzinfo is None:
                    deadline = deadline.replace(tzinfo=UTC)
            except ValueError:
                deadline = None

        analysis = ImpactAnalysis(
            change_event_id=change.id,
            root_kind=root_kind,
            root_id=root_id,
            classification=classification,
            deadline_at=deadline,
        )
        self.db.add(analysis)
        await self.db.flush()

        items, truncated = await self._traverse(root_kind, root_id)
        summary: dict = {"truncated": truncated}
        action = _CLASSIFICATION_ACTION[classification]
        for (node_kind, node_id), (depth, path) in items.items():
            summary[node_kind] = summary.get(node_kind, 0) + 1
            self.db.add(
                ImpactItem(
                    analysis_id=analysis.id,
                    node_kind=node_kind,
                    node_id=node_id,
                    depth=depth,
                    path=path,
                    active_usage=await self._active_usage(node_kind, node_id),
                    recommended_action=action,
                )
            )
        analysis.summary = summary
        await self.db.flush()
        return analysis

    async def _traverse(
        self, root_kind: str, root_id: str
    ) -> tuple[dict[tuple[str, str], tuple[int, list]], bool]:
        """Cycle-safe BFS: dependency -> dependents, capped depth & node count."""
        visited: set[tuple[str, str]] = {(root_kind, root_id)}
        result: dict[tuple[str, str], tuple[int, list]] = {}
        queue: deque = deque([((root_kind, root_id), 0, [])])
        truncated = False
        while queue:
            (kind, node_id), depth, path = queue.popleft()
            if depth >= IMPACT_MAX_DEPTH:
                continue
            edges = await self.db.scalars(
                select(DependencyEdge).where(
                    DependencyEdge.to_kind == kind, DependencyEdge.to_id == node_id
                )
            )
            for edge in edges:
                key = (edge.from_kind, edge.from_id)
                if key in visited:
                    continue  # cycle safety
                visited.add(key)
                if len(result) >= IMPACT_MAX_NODES:
                    truncated = True
                    return result, truncated
                new_path = path + [edge.id]
                result[key] = (depth + 1, new_path)
                queue.append((key, depth + 1, new_path))
        return result, truncated

    async def _active_usage(self, node_kind: str, node_id: str) -> dict:
        """Live usage counts for product components (best-effort, cheap)."""
        usage: dict = {}
        try:
            if node_kind == "workflow_pack":
                from app.models.workflow_pack import WorkflowPackInstallation

                count = await self.db.scalar(
                    select(func.count())
                    .select_from(WorkflowPackInstallation)
                    .where(WorkflowPackInstallation.pack_id == node_id)
                )
                usage["installations"] = count or 0
            elif node_kind == "cohort":
                usage["active_cohorts"] = 1
        except Exception:  # noqa: BLE001 — usage enrichment must never break analysis
            pass
        return usage

    async def get(self, analysis_id: str) -> tuple[ImpactAnalysis, list[ImpactItem]]:
        analysis = await self.db.get(ImpactAnalysis, analysis_id)
        if not analysis:
            raise AppError("NOT_FOUND", "Impact analysis not found", 404)
        items = await self.db.scalars(
            select(ImpactItem)
            .where(ImpactItem.analysis_id == analysis_id)
            .order_by(ImpactItem.depth, ImpactItem.node_kind)
        )
        return analysis, list(items)

    async def list(
        self,
        *,
        status: str | None = None,
        classification: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ImpactAnalysis]:
        query = select(ImpactAnalysis)
        if status:
            query = query.where(ImpactAnalysis.status == status)
        if classification:
            if classification not in IMPACT_CLASSIFICATIONS:
                raise AppError("VALIDATION_ERROR", "Unknown classification", 422)
            query = query.where(ImpactAnalysis.classification == classification)
        rows = await self.db.scalars(
            query.order_by(ImpactAnalysis.computed_at.desc()).limit(limit).offset(offset)
        )
        return list(rows)

    async def set_status(self, analysis_id: str, status: str) -> ImpactAnalysis:
        if status not in ("open", "acknowledged", "resolved"):
            raise AppError("VALIDATION_ERROR", f"Unknown status: {status}", 422)
        analysis = await self.db.get(ImpactAnalysis, analysis_id)
        if not analysis:
            raise AppError("NOT_FOUND", "Impact analysis not found", 404)
        analysis.status = status
        await self.db.flush()
        return analysis
