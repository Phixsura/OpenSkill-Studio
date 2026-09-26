"""Round-39 tests (ADR-016 §45): concurrent draft publish has exactly one winner."""

import asyncio

import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.ecosystem.services.drafts import DraftService
from app.exceptions import AppError
from tests.test_eco_services_db import _mk_org, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def test_concurrent_publish_materializes_exactly_once(db):
    creator = await _mk_user(db, "admin")
    approver = await _mk_user(db, "admin")
    org = await _mk_org(db)
    svc = DraftService(db)
    draft = await svc.create(
        draft_type="workflow_pack", title="race-pack",
        payload={
            "name": "RacePack",
            "definition": {"steps": [{"id": "s1", "capability": "image_generation"}]},
        },
        created_by=creator.id, org_id=org.id,
    )
    await svc.transition(draft.id, to_status="in_review", actor_id=creator.id, org_id=org.id)
    await svc.transition(draft.id, to_status="approved", actor_id=approver.id, org_id=org.id)
    await db.commit()  # visible to the racing sessions
    draft_id, approver_id, org_id = draft.id, approver.id, org.id

    async def publish_once():
        async with AsyncSessionLocal() as session:
            try:
                await DraftService(session).transition(
                    draft_id, to_status="published", actor_id=approver_id, org_id=org_id
                )
                await session.commit()
                return "published"
            except AppError as exc:
                await session.rollback()
                return exc.code

    results = await asyncio.gather(publish_once(), publish_once())
    assert sorted(results) == ["ECO_DRAFT_NOT_APPROVED", "published"], results

    # Exactly ONE materialized pack
    from app.models.workflow_pack import WorkflowPack

    async with AsyncSessionLocal() as session:
        packs = list(await session.scalars(
            select(WorkflowPack).where(WorkflowPack.owner_org_id == org_id,
                                       WorkflowPack.name == "RacePack")
        ))
        # cleanup so repeated local runs stay green
        draft_row = await session.get(
            (await _draft_model()), draft_id
        )
        assert len(packs) == 1
        assert draft_row.published_ref == packs[0].id


async def _draft_model():
    from app.ecosystem.models.replacement import ComponentDraft

    return ComponentDraft
