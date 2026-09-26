"""Round-12 tests (ADR-016 §21): Pareto frontier flags + Atom change feed."""

from datetime import UTC, datetime

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.ecosystem.models.benchmark import BenchmarkRun
from app.ecosystem.models.catalog import AIModel
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.services.benchmark import BenchmarkService
from tests.test_eco_services_db import _mk_source, _mk_suite_with_cases, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_completed_run(db, suite, name, quality, cost):
    model = AIModel(canonical_name=name, slug=f"{name.lower()}-{str(ULID()).lower()}")
    db.add(model)
    await db.flush()
    run = BenchmarkRun(
        suite_id=suite.id,
        status="completed",
        target={"entity_kind": "model", "entity_id": model.id},
        dimension_scores={"reliability": quality},
        total_cost_usd=cost,
        finished_at=datetime.now(UTC),
    )
    db.add(run)
    await db.flush()
    return model


async def test_leaderboard_pareto_frontier_flags(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    # frontier: best quality (0.9/$5), cheapest (0.5/$1)
    # dominated: 0.6/$4 (CheapGood has higher quality at lower cost? 0.5<0.6 no —
    #   dominated by Mid? Mid=0.8/$2 dominates 0.6/$4: higher quality, lower cost)
    top = await _mk_completed_run(db, suite, "TopGen", 0.9, 5.0)
    mid = await _mk_completed_run(db, suite, "MidGen", 0.8, 2.0)
    cheap = await _mk_completed_run(db, suite, "CheapGen", 0.5, 1.0)
    dominated = await _mk_completed_run(db, suite, "DominatedGen", 0.6, 4.0)

    board = await BenchmarkService(db).leaderboard(
        suite_id=suite.id, dimension="reliability"
    )
    flags = {r["canonical_name"]: r.get("on_frontier") for r in board["rows"]}
    assert flags["TopGen"] is True
    assert flags["MidGen"] is True
    assert flags["CheapGen"] is True
    assert flags["DominatedGen"] is False
    # Ranked by quality desc regardless of frontier
    assert [r["canonical_name"] for r in board["rows"]][:2] == ["TopGen", "MidGen"]
    assert len({top.id, mid.id, cheap.id, dominated.id}) == 4  # distinct entities


async def test_leaderboard_frontier_skipped_for_cost_dimension(db):
    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin)
    await _mk_completed_run(db, suite, "OnlyGen", 0.7, 1.0)
    board = await BenchmarkService(db).leaderboard(
        suite_id=suite.id, dimension="cost_per_case_usd"
    )
    assert all("on_frontier" not in r for r in board["rows"])


async def test_atom_feed_escapes_untrusted_change_content(db):
    from app.ecosystem.api.dashboard import export_changes_atom
    from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
    from tests.test_eco_services_db import _mk_source

    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        raw_hash="a" * 64, normalized={},
    )
    db.add(obs)
    await db.flush()
    db.add(ChangeEvent(
        observation_id=obs.id, change_type="price",
        field='<script>alert("x")</script>',
        old_value={"v": 1}, new_value={"v": "2 < 3 & 4"},
        severity="info",
    ))
    await db.flush()

    resp = await export_changes_atom(severity=None, limit=50, db=db, _user=None)
    body = resp.body.decode()
    assert resp.media_type == "application/atom+xml"
    assert "<script>" not in body  # untrusted content XML-escaped
    assert "&lt;script&gt;" in body
    assert "urn:openskill:eco-change:" in body

async def test_suite_export_import_roundtrip(db):
    from app.ecosystem.services.benchmark import BenchmarkService
    from app.exceptions import AppError as _AppError

    admin = await _mk_user(db, "admin")
    suite = await _mk_suite_with_cases(db, admin, n_cases=3)
    svc = BenchmarkService(db)

    doc = await svc.export_suite(suite.id)
    assert doc["format"] == "openskill.benchmark-suite"
    assert len(doc["cases"]) == 3
    assert len(doc["cases_fingerprint"]) == 64
    assert "runs" not in doc  # results never travel

    # Same key collides — never silently merged
    import pytest as _pytest
    with _pytest.raises(_AppError) as exc:
        await svc.import_suite(doc, created_by=admin.id)
    assert exc.value.code == "ECO_SUITE_EXISTS"

    # New key imports cleanly with identical case content
    doc["suite"]["key"] = doc["suite"]["key"] + "-copy"
    imported = await svc.import_suite(doc, created_by=admin.id)
    assert imported.status == "draft"
    re_exported = await svc.export_suite(imported.id)
    assert re_exported["cases_fingerprint"] != ""  # fingerprint computed
    assert [c["prompt"] for c in re_exported["cases"]] == [
        c["prompt"] for c in doc["cases"]
    ]

    # Garbage documents rejected
    with _pytest.raises(_AppError):
        await svc.import_suite({"format": "something-else"}, created_by=admin.id)
    with _pytest.raises(_AppError):
        await svc.import_suite(
            {"format": "openskill.benchmark-suite", "version": 1,
             "suite": {"key": "x"}, "cases": []},
            created_by=admin.id,
        )

async def test_atom_feed_filters_by_entity(db):
    """Round-157 killer: ?entity_id narrows the Atom feed to ONE canonical
    entity (GitHub releases.atom posture) — other entities' changes are
    excluded and the XML stays escaped."""
    from app.ecosystem.api.dashboard import export_changes_atom

    source = await _mk_source(db)
    tag = str(ULID()).lower()[:6]
    wanted = AIModel(canonical_name=f"AtomA-{tag}", slug=f"aa-{tag}")
    other = AIModel(canonical_name=f"AtomB-{tag}", slug=f"ab-{tag}")
    db.add_all([wanted, other])
    await db.flush()
    for model, marker in ((wanted, f"WANTED-{tag}"), (other, f"OTHER-{tag}")):
        obs = EcosystemObservation(
            source_id=source.id, event_type="catalog_snapshot",
            canonical_entity_kind="model", canonical_entity_id=model.id,
            raw_hash=(str(ULID()).lower() * 3)[:64], normalized={},
        )
        db.add(obs)
        await db.flush()
        db.add(ChangeEvent(
            observation_id=obs.id, change_type="license", field="license",
            old_value={"value": marker}, new_value={"value": "<x&y>"},
            severity="breaking", entity_kind="model", canonical_entity_id=model.id,
        ))
    await db.flush()

    resp = await export_changes_atom(
        severity=None, entity_id=wanted.id, limit=50, db=db, _user=None
    )
    body = resp.body.decode()
    assert f"WANTED-{tag}" in body
    assert f"OTHER-{tag}" not in body
    assert "<x&y>" not in body  # escaped, never raw
    assert "&lt;x&amp;y&gt;" in body


async def test_atom_feed_survives_control_chars_and_is_wellformed(db):
    """Round-230 killer: control chars are legal in Postgres text/JSONB but
    ILLEGAL in XML 1.0 — saxutils.escape passes them through, so ONE poisoned
    observation made the whole feed unparseable for every consumer. The feed
    must stay well-formed XML with the control char stripped."""
    import xml.etree.ElementTree as ET

    from app.ecosystem.api.dashboard import export_changes_atom
    from tests.test_eco_services_db import _mk_source

    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        raw_hash="b" * 64, normalized={},
    )
    db.add(obs)
    await db.flush()
    db.add(ChangeEvent(
        observation_id=obs.id, change_type="price",
        field="ver\x08sion",  # backspace: valid in PG, invalid in XML 1.0
        old_value={"v": "a\x01b"}, new_value={"v": 2},
        severity="info",
    ))
    await db.flush()

    resp = await export_changes_atom(severity=None, limit=50, db=db, _user=None)
    root = ET.fromstring(resp.body.decode())  # would raise before the fix
    ns = "{http://www.w3.org/2005/Atom}"
    titles = [t.text for t in root.iter(f"{ns}title")]
    assert any("version" in (t or "") for t in titles)  # char stripped, not row dropped
    # Atom 1.0 spec: feed-level author is required
    assert root.find(f"{ns}author/{ns}name") is not None


async def test_atom_feed_empty_result_still_valid_atom(db):
    """Round-230: an empty feed must still carry a non-empty RFC3339
    <updated> (Atom requires it; \'\' is spec-invalid and breaks readers)."""
    import xml.etree.ElementTree as ET

    from app.ecosystem.api.dashboard import export_changes_atom

    tag = str(ULID()).lower()[:6]
    lonely = AIModel(canonical_name=f"AtomEmpty-{tag}", slug=f"ae-{tag}")
    db.add(lonely)
    await db.flush()
    resp = await export_changes_atom(
        severity=None, entity_id=lonely.id, limit=50, db=db, _user=None
    )
    root = ET.fromstring(resp.body.decode())
    ns = "{http://www.w3.org/2005/Atom}"
    updated = root.find(f"{ns}updated")
    assert updated is not None and updated.text  # non-empty timestamp
    assert root.find(f"{ns}author/{ns}name") is not None


async def test_change_feed_order_is_deterministic_on_timestamp_ties(db):
    """Round-289 killer: batch-inserted changes share server-default now() —
    without an id tiebreak the feed order (and therefore the Atom ETag
    window) flaps between identical queries. Same-timestamp rows must come
    back newest-id-first, stably."""
    from datetime import UTC, datetime

    from app.ecosystem.services.dashboard import DashboardService
    from tests.test_eco_services_db import _mk_source

    source = await _mk_source(db)
    obs = EcosystemObservation(
        source_id=source.id, event_type="pricing_changed",
        raw_hash="d" * 64, normalized={},
    )
    db.add(obs)
    await db.flush()
    ts = datetime(2026, 9, 27, 3, 0, tzinfo=UTC)
    ids = []
    for i in range(5):
        c = ChangeEvent(
            observation_id=obs.id, change_type="price",
            field=f"tie-{i}", old_value={"v": i}, new_value={"v": i + 1},
            severity="info", detected_at=ts,
        )
        db.add(c)
        await db.flush()
        ids.append(c.id)

    svc = DashboardService(db)
    first = [c.id for c in await svc.change_feed(limit=200)]
    second = [c.id for c in await svc.change_feed(limit=200)]
    assert first == second  # deterministic across identical queries
    # within the tie: newest ULID first (descending id)
    ours_in_feed = [i for i in first if i in set(ids)]
    assert ours_in_feed == sorted(ids, reverse=True)
