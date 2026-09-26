"""Round-65 tests (ADR-016 §58): export-format compliance & injection."""

from datetime import UTC, datetime, timedelta

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.catalog import AIModel
from tests.test_eco_services_db import _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def test_ics_names_cannot_inject_properties(db):
    """A hostile entity name with newlines/commas must never fold into new
    ICS property lines (RFC 5545 escaping)."""
    from app.ecosystem.api.catalog import deprecation_calendar_ics
    from app.ecosystem.models.catalog import ModelVersion

    parent = AIModel(canonical_name="EvilParent", slug=f"evp-{str(ULID()).lower()}")
    db.add(parent)
    await db.flush()
    evil = ModelVersion(
        model_id=parent.id,
        version="6.6.6",
        canonical_name="Evil\nATTENDEE:mailto:x@evil\nSUMMARY:Injected, one; two",
        lifecycle_status="deprecated",
        sunset_at=datetime.now(UTC) + timedelta(days=30),
    )
    db.add(evil)
    await db.flush()
    resp = await deprecation_calendar_ics(within_days=90, db=db, _user=None)
    body = resp.body.decode()
    # No raw injected property line...
    assert "\nATTENDEE:mailto:x@evil" not in body.replace("\r\n", "\n")
    # ...the newline arrives escaped inside the SUMMARY value instead
    assert "\\nATTENDEE" in body
    assert "Injected\\, one\\; two" in body


async def test_ops_metrics_every_sample_has_matching_type_line(db):
    """Prometheus exposition compliance: every emitted sample name must carry
    its OWN `# TYPE <name> gauge` line — a TYPE for a name that never appears
    leaves all real metrics untyped."""
    from app.ecosystem.api.dashboard import ops_metrics

    admin = await _mk_user(db, "admin")
    resp = await ops_metrics(db=db, _user=admin)
    text = resp.body.decode()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    samples = [ln.split(" ")[0] for ln in lines if not ln.startswith("#")]
    types = {
        ln.split(" ")[2]
        for ln in lines
        if ln.startswith("# TYPE") and ln.endswith("gauge")
    }
    assert samples, "no metrics emitted"
    for name in samples:
        assert name in types, f"sample {name} lacks a matching TYPE line"
    # And no orphan TYPE lines for names that never appear
    assert types == set(samples)

async def test_catalog_export_is_complete_beyond_100_entities(db):
    """Round-168 killer: the export is the integration currency — a catalog
    kind with >100 entities must export ALL of them (with per-kind totals),
    not a silently-truncated first page."""
    from app.ecosystem.api.catalog import catalog_export

    tag = str(ULID()).lower()[:6]
    for i in range(105):
        db.add(AIModel(canonical_name=f"Bulk{tag}-{i:03d}", slug=f"bk{tag}-{i:03d}"))
    await db.flush()

    out = (await catalog_export(db=db, _user=None))["data"]
    names = {e["canonical_name"] for e in out["entities"]["models"]}
    exported = [n for n in names if n.startswith(f"Bulk{tag}-")]
    assert len(exported) == 105, f"exported only {len(exported)} of 105"
    assert out["entity_totals"]["models"] >= 105
    assert out["truncated"] is False
