"""P12 outbox infrastructure tests (ADR-014 cross-cutting):
same-tx atomicity, handler idempotency, backoff, dead-letter, SKIP LOCKED."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.outbox import OutboxMessage, enqueue
from app.controlplane.worker import (
    HANDLERS,
    load_handlers,
    process_outbox_once,
    reap_stuck,
    register_handler,
)
from app.core.database import AsyncSessionLocal


@pytest.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture
def test_topic():
    """Register a throwaway handler topic; clean up after."""
    topic = f"test.{str(ULID()).lower()[-8:]}"
    yield topic
    HANDLERS.pop(topic, None)


# ── Atomicity ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_enqueue_rolls_back_with_business_tx(db, test_topic):
    """The outbox INSERT lives in the caller's transaction: rollback → gone."""
    enqueue(db, test_topic, {"n": 1})
    await db.flush()
    await db.rollback()
    async with AsyncSessionLocal() as check:
        count = (
            (await check.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic)))
            .scalars()
            .all()
        )
        assert count == []


# ── Processing semantics ─────────────────────────────────────


@pytest.mark.asyncio
async def test_process_success_and_idempotent_handler(test_topic):
    from app.core.database import engine

    calls: list[dict] = []

    @register_handler(test_topic)
    async def _handler(session, payload):  # noqa: ARG001
        calls.append(payload)

    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, test_topic, {"k": "v"})
            await db.commit()
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[test_topic])
            assert handled == 1
        # Second pass: nothing pending → handler not re-invoked
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[test_topic])
            assert handled == 0
        assert calls == [{"k": "v"}]
        async with AsyncSessionLocal() as db:
            msg = (
                await db.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic))
            ).scalar_one()
            assert msg.status == "done" and msg.processed_at is not None
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_failure_backs_off_then_dead_letters(test_topic, monkeypatch):
    from app.config import settings
    from app.core.database import engine

    monkeypatch.setattr(settings, "outbox_max_attempts", 3)

    @register_handler(test_topic)
    async def _handler(session, payload):  # noqa: ARG001
        raise RuntimeError("boom")

    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, test_topic, {})
            await db.commit()

        for attempt in range(1, 4):
            # Make the message due despite exponential backoff
            async with AsyncSessionLocal() as db:
                msg = (
                    await db.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic))
                ).scalar_one()
                msg.available_at = datetime.now(UTC) - timedelta(seconds=1)
                await db.commit()
            async with AsyncSessionLocal() as db:
                await process_outbox_once(db, topics=[test_topic])
            async with AsyncSessionLocal() as db:
                msg = (
                    await db.execute(select(OutboxMessage).where(OutboxMessage.topic == test_topic))
                ).scalar_one()
                assert msg.attempts == attempt
                assert "boom" in (msg.last_error or "")
                if attempt < 3:
                    assert msg.status == "pending"
                    # Exponential backoff pushed available_at into the future
                    assert msg.available_at.replace(tzinfo=UTC) > datetime.now(UTC)
                else:
                    assert msg.status == "failed"  # dead-lettered
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_unknown_topic_backs_off_without_burning_attempts():
    from app.core.database import engine

    topic = f"test.unknown.{str(ULID()).lower()[-8:]}"
    try:
        async with AsyncSessionLocal() as db:
            enqueue(db, topic, {})
            await db.commit()
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db, topics=[topic])
            assert handled == 0
        async with AsyncSessionLocal() as db:
            msg = (
                await db.execute(select(OutboxMessage).where(OutboxMessage.topic == topic))
            ).scalar_one()
            assert msg.status == "pending" and msg.attempts == 0
    finally:
        await engine.dispose()


# ── Concurrency (SKIP LOCKED) ────────────────────────────────


@pytest.mark.asyncio
async def test_dual_worker_no_double_consumption(test_topic):
    """Two concurrent workers over the same batch: each message handled once."""
    from app.core.database import engine

    calls: list[int] = []

    @register_handler(test_topic)
    async def _handler(session, payload):  # noqa: ARG001
        await asyncio.sleep(0.05)  # widen the race window
        calls.append(payload["i"])

    try:
        async with AsyncSessionLocal() as db:
            for i in range(6):
                enqueue(db, test_topic, {"i": i})
            await db.commit()

        async def worker():
            async with AsyncSessionLocal() as session:
                return await process_outbox_once(session, topics=[test_topic])

        results = await asyncio.gather(worker(), worker())
        assert sum(results) == 6  # split between workers, never doubled
        assert sorted(calls) == [0, 1, 2, 3, 4, 5]
    finally:
        await engine.dispose()


# ── Reaper ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reaper_returns_stuck_processing_to_pending():
    from app.core.database import engine

    topic = f"test.stuck.{str(ULID()).lower()[-8:]}"
    try:
        async with AsyncSessionLocal() as db:
            msg = enqueue(db, topic, {})
            await db.flush()
            msg.status = "processing"
            msg.locked_by = "dead-worker"
            msg.locked_at = datetime.now(UTC) - timedelta(minutes=30)
            await db.commit()
            mid = msg.id
        async with AsyncSessionLocal() as db:
            reaped = await reap_stuck(db, older_than_minutes=10)
            assert reaped >= 1
            await db.commit()
        async with AsyncSessionLocal() as db:
            msg = await db.get(OutboxMessage, mid)
            assert msg.status == "pending" and msg.locked_by is None
    finally:
        await engine.dispose()


def test_all_production_handlers_registered():
    load_handlers()
    expected = {
        "usage.recorded",
        "fx.rate_created",
        "run.terminal",
        "period.close_due",
        "invoice.finalized",
        "purchase.paid",
        "purchase.refunded",
        "credit_note.applied",
        "provision.run",
    }
    assert expected <= set(HANDLERS.keys())
