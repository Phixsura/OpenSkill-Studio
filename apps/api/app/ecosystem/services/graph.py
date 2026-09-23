"""Dependency graph (ADR-016 Part H).

Edges point FROM a dependent component TO its dependency:
    workflow_pack_release --requires_capability--> capability
Impact traversal walks edges in reverse (dependency -> dependents).
Never auto-installs anything — the graph is metadata only.
"""

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.graph import (
    CONSTRAINT_TYPES,
    GRAPH_NODE_KINDS,
    DependencyEdge,
)
from app.exceptions import AppError


class GraphService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_edge(
        self,
        *,
        from_kind: str,
        from_id: str,
        to_kind: str,
        to_id: str,
        constraint_type: str = "uses",
        constraint_spec: dict | None = None,
        org_id: str | None = None,
    ) -> DependencyEdge:
        for kind in (from_kind, to_kind):
            if kind not in GRAPH_NODE_KINDS:
                raise AppError("VALIDATION_ERROR", f"Unknown node kind: {kind}", 422)
        if constraint_type not in CONSTRAINT_TYPES:
            raise AppError("VALIDATION_ERROR", f"Unknown constraint type: {constraint_type}", 422)
        if from_kind == to_kind and from_id == to_id:
            raise AppError("VALIDATION_ERROR", "Self-edges are not allowed", 422)
        stmt = (
            pg_insert(DependencyEdge)
            .values(
                from_kind=from_kind,
                from_id=from_id,
                to_kind=to_kind,
                to_id=to_id,
                constraint_type=constraint_type,
                constraint_spec=constraint_spec or {},
                org_id=org_id,
            )
            .on_conflict_do_nothing(constraint="uq_eco_dep_edge")
            .returning(DependencyEdge.id)
        )
        edge_id = await self.db.scalar(stmt)
        if edge_id is None:
            existing = await self.db.scalar(
                select(DependencyEdge).where(
                    DependencyEdge.from_kind == from_kind,
                    DependencyEdge.from_id == from_id,
                    DependencyEdge.to_kind == to_kind,
                    DependencyEdge.to_id == to_id,
                    DependencyEdge.constraint_type == constraint_type,
                )
            )
            return existing
        return await self.db.get(DependencyEdge, edge_id)

    async def remove_edge(self, edge_id: str, *, org_id: str | None = None) -> None:
        edge = await self.db.get(DependencyEdge, edge_id)
        if not edge:
            raise AppError("NOT_FOUND", "Edge not found", 404)
        # Org-scoped edges may only be removed within the owning org (uniform 404)
        if edge.org_id is not None and org_id is not None and edge.org_id != org_id:
            raise AppError("NOT_FOUND", "Edge not found", 404)
        await self.db.delete(edge)
        await self.db.flush()

    async def edges_for_node(
        self, kind: str, node_id: str, *, org_id: str | None = None
    ) -> dict:
        """Both directions for one node, private edges filtered by org."""
        visibility = or_(DependencyEdge.org_id.is_(None), DependencyEdge.org_id == org_id)
        outgoing = await self.db.scalars(
            select(DependencyEdge).where(
                DependencyEdge.from_kind == kind,
                DependencyEdge.from_id == node_id,
                visibility,
            )
        )
        incoming = await self.db.scalars(
            select(DependencyEdge).where(
                DependencyEdge.to_kind == kind,
                DependencyEdge.to_id == node_id,
                visibility,
            )
        )
        return {"depends_on": list(outgoing), "dependents": list(incoming)}

    async def dependents_of(
        self, kind: str, node_id: str, *, include_private: bool = True
    ) -> list[DependencyEdge]:
        """All edges whose dependency is this node (reverse traversal step)."""
        query = select(DependencyEdge).where(
            DependencyEdge.to_kind == kind, DependencyEdge.to_id == node_id
        )
        if not include_private:
            query = query.where(DependencyEdge.org_id.is_(None))
        rows = await self.db.scalars(query)
        return list(rows)

    async def sync_release_edges(self, release_id: str) -> int:
        """Derive capability edges from a WorkflowPackRelease's definition."""
        from app.models.workflow_pack import WorkflowPackRelease

        release = await self.db.get(WorkflowPackRelease, release_id)
        if not release:
            raise AppError("NOT_FOUND", "Release not found", 404)
        # A release snapshots the definition INSIDE its manifest — the model
        # has no .definition attribute, so the old attribute access raised
        # AttributeError (HTTP 500) for every real release (zero tests hid it)
        definition = (release.manifest or {}).get("definition") or {}
        steps = definition.get("steps") or []
        created = 0
        seen: set[str] = set()
        for step in steps:
            if not isinstance(step, dict):
                continue
            cap = step.get("capability")
            if not isinstance(cap, str) or cap in seen:
                continue
            seen.add(cap)
            await self.add_edge(
                from_kind="workflow_pack_release",
                from_id=release.id,
                to_kind="capability",
                to_id=cap[:26],
                constraint_type="requires_capability",
                constraint_spec={"capability_key": cap},
            )
            created += 1
        # Pack -> release containment edge
        await self.add_edge(
            from_kind="workflow_pack",
            from_id=release.pack_id,
            to_kind="workflow_pack_release",
            to_id=release.id,
            constraint_type="uses",
        )
        return created
