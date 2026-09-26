"""Round-36 tests (ADR-016 §42): raw snapshot retention + parser replay."""

import json

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.observation import EcosystemObservation
from app.ecosystem.models.source import RawSnapshot
from app.ecosystem.services.sync import SyncService
from tests.test_eco_services_db import _mk_source


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _payload(name, version="1.0"):
    return json.dumps(
        {"models": [{"official_id": f"{name}", "name": name, "version": version}]}
    ).encode()


async def test_sync_retains_snapshot_and_replay_is_idempotent(db):
    source = await _mk_source(db, adapter_key="manual")
    svc = SyncService(db)
    body = _payload(f"gen-{str(ULID()).lower()[:8]}")
    run = await svc.run_sync(source.id, raw_payload=body)
    assert run.status == "success"
    snap = await db.scalar(
        select(RawSnapshot).where(RawSnapshot.source_id == source.id)
    )
    assert snap is not None and snap.content == body

    # Replay with the SAME parser: everything unchanged, nothing new
    out = await svc.replay_source(source.id)
    assert out["snapshots"] == 1
    assert out["created"] == 0
    assert out["superseded"] == 0
    assert out["unchanged"] >= 1


async def test_parser_upgrade_replay_supersedes_never_rewrites(db):
    source = await _mk_source(db, adapter_key="manual")
    svc = SyncService(db)
    name = f"gen-{str(ULID()).lower()[:8]}"
    await svc.run_sync(source.id, raw_payload=_payload(name))
    original = await db.scalar(
        select(EcosystemObservation).where(EcosystemObservation.source_id == source.id)
    )
    assert original is not None
    original_normalized = dict(original.normalized)

    # Simulate a parser upgrade that changes normalized output
    from app.ecosystem.services import sync as sync_mod

    adapter = sync_mod.ADAPTERS[source.adapter_key]
    real_parse = adapter.parse

    def upgraded_parse(body, config):
        items = real_parse(body, config)
        for item in items:
            item.normalized = {**item.normalized, "upgraded": True}
        return items

    source.parser_version = "2.0"
    await db.flush()
    adapter.parse = upgraded_parse
    try:
        out = await svc.replay_source(source.id)
    finally:
        adapter.parse = real_parse

    assert out["superseded"] == 1
    await db.refresh(original)
    # Old row NEVER rewritten — only linked forward
    assert original.normalized == original_normalized
    assert original.superseded_by_id is not None
    replacement = await db.get(EcosystemObservation, original.superseded_by_id)
    assert replacement.normalized.get("upgraded") is True
    assert replacement.parser_version == "2.0"
    assert replacement.human_verified is False  # new content needs fresh review
    # Curated resolution inherited
    assert replacement.canonical_entity_id == original.canonical_entity_id

    # Second replay with the same parser: no double-supersede
    adapter.parse = upgraded_parse
    try:
        out2 = await svc.replay_source(source.id)
    finally:
        adapter.parse = real_parse
    assert out2["superseded"] == 0
